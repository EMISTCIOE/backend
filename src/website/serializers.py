from django.core.files.storage import default_storage
from django.utils.text import slugify
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from src.base.serializers import AbstractInfoRetrieveSerializer

# Project Imports
from src.core.models import FiscalSessionBS
from src.department.models import Department
from src.libs.get_context import get_user_by_context
from src.libs.mixins import FileHandlingMixin
from src.website.validators import (
    validate_campus_download_file,
    validate_photo_thumbnail,
)

from .messages import (
    ACADEMIC_CALENDER_CREATED_SUCCESS,
    ACADEMIC_CALENDER_UPDATED_SUCCESS,
    CAMPUS_CLUB_CREATED_SUCCESS,
    CAMPUS_CLUB_UPDATED_SUCCESS,
    CAMPUS_DOWNLOAD_CREATED_SUCCESS,
    CAMPUS_DOWNLOAD_UPDATED_SUCCESS,
    CAMPUS_EVENT_CREATED_SUCCESS,
    CAMPUS_EVENT_UPDATED_SUCCESS,
    CAMPUS_INFO_UPDATED_SUCCESS,
    CAMPUS_KEY_OFFICIAL_CREATE_SUCCESS,
    CAMPUS_KEY_OFFICIAL_UPDATE_SUCCESS,
    CAMPUS_REPORT_CREATED_SUCCESS,
    CAMPUS_REPORT_UPDATED_SUCCESS,
    CAMPUS_SECTION_CREATED_SUCCESS,
    CAMPUS_SECTION_UPDATED_SUCCESS,
    CAMPUS_UNION_CREATED_SUCCESS,
    CAMPUS_UNION_UPDATED_SUCCESS,
    CAMPUS_UNIT_CREATED_SUCCESS,
    CAMPUS_UNIT_UPDATED_SUCCESS,
    EVENT_DATE_ERROR,
    GLOBAL_EVENT_CREATED_SUCCESS,
    GLOBAL_EVENT_UPDATED_SUCCESS,
    RESEARCH_FACILITY_CREATED_SUCCESS,
    RESEARCH_FACILITY_UPDATED_SUCCESS,
    SOCIAL_MEDIA_ALREADY_EXISTS,
    YEAR_ORDER_ERROR,
)
from .models import (
    AcademicCalendar,
    CampusDownload,
    CampusFeedback,
    CampusInfo,
    CampusKeyOfficial,
    CampusReport,
    CampusSection,
    CampusStaffDesignation,
    CampusUnion,
    CampusUnionMember,
    CampusUnit,
    GlobalEvent,
    GlobalGalleryImage,
    ResearchFacility,
    SocialMediaLink,
    StudentClub,
    StudentClubMember,
)
from .utils import resolve_gallery_image_source


class DepartmentSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "uuid", "name"]


def _validate_designation_codes(codes):
    if not codes:
        return []

    cleaned_codes = [code for code in codes if code]
    if not cleaned_codes:
        return []

    existing_codes = set(
        CampusStaffDesignation.objects.filter(code__in=cleaned_codes).values_list(
            "code",
            flat=True,
        ),
    )
    invalid_codes = sorted(
        {code for code in cleaned_codes if code not in existing_codes},
    )
    if invalid_codes:
        raise serializers.ValidationError(
            f"Invalid designation codes: {', '.join(invalid_codes)}",
        )

    # Preserve original order while removing duplicates
    return list(dict.fromkeys(cleaned_codes))


# Campus Info Serializers
# ---------------------------------------------------------------------------------------------------


class SocialMediaLinkListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaLink
        fields = ["id", "platform", "url", "is_active"]


class CampusInfoRetrieveSerializer(serializers.ModelSerializer):
    social_links = serializers.SerializerMethodField()

    class Meta:
        model = CampusInfo
        fields = [
            "name",
            "phone_number",
            "email",
            "location",
            "organization_chart",
            "social_links",
        ]

    @extend_schema_field(SocialMediaLinkListSerializer(many=True))
    def get_social_links(self, obj):
        return SocialMediaLinkListSerializer(
            SocialMediaLink.objects.filter(is_active=True),
            many=True,
        ).data


class SocialMediaLinkPatchSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=SocialMediaLink.objects.filter(is_archived=False),
        required=False,
    )

    class Meta:
        model = SocialMediaLink
        fields = ["id", "platform", "url", "is_active"]


class CampusInfoPatchSerializer(serializers.ModelSerializer):
    social_links = SocialMediaLinkPatchSerializer(many=True)

    class Meta:
        model = CampusInfo
        fields = [
            "name",
            "phone_number",
            "email",
            "location",
            "organization_chart",
            "social_links",
        ]

    def validate(self, attrs):
        social_links = attrs.get("social_links", [])

        for social_link in social_links:
            media_ins = SocialMediaLink.objects.filter(platform=social_link["platform"])
            if "id" in social_link:
                if media_ins.exclude(pk=social_link["id"].id).exists():
                    raise serializers.ValidationError(
                        {"message": SOCIAL_MEDIA_ALREADY_EXISTS},
                    )
            elif media_ins.exists():
                raise serializers.ValidationError(
                    {"message": SOCIAL_MEDIA_ALREADY_EXISTS},
                )

        return attrs

    def update(self, instance, validated_data):
        user = get_user_by_context(self.context)
        social_links = validated_data.pop("social_links", [])

        if "name" in validated_data:
            validated_data["name"] = validated_data.pop("name").strip().title()

        for key, val in validated_data.items():
            setattr(instance, key, val)

        for social_link in social_links:
            sl = social_link.pop("id", None)
            if sl:
                # Update the social media link instance
                for key, val in social_link.items():
                    setattr(sl, key, val)
                sl.updated_by = user
                sl.save()
            else:
                # Create new social media link
                SocialMediaLink.objects.create(**social_link, created_by=user)

        instance.updated_by = user
        instance.save()
        return instance

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": CAMPUS_INFO_UPDATED_SUCCESS}


# Campus Key Official Serializers
# ---------------------------------------------------------------------------------------------------


class CampusKeyOfficialListSerializer(serializers.ModelSerializer):
    designation = serializers.SlugRelatedField(
        read_only=True,
        slug_field="code",
    )
    designation_display = serializers.CharField(
        source="designation.title",
        read_only=True,
    )
    title_prefix_display = serializers.CharField(
        source="get_title_prefix_display",
        read_only=True,
    )
    # Return department OR unit in the department field (only one can exist)
    department = serializers.SerializerMethodField()
    program = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()

    class Meta:
        model = CampusKeyOfficial
        fields = [
            "uuid",
            "id",
            "title_prefix",
            "title_prefix_display",
            "full_name",
            "designation",
            "designation_display",
            "photo",
            "email",
            "phone_number",
            "is_key_official",
            "is_active",
            "department",
            "program",
            "unit",
            "display_order",
        ]

    def get_department(self, obj):
        """Return department info if exists, otherwise return unit info."""
        if obj.department:
            return {
                "id": obj.department.id,
                "uuid": str(obj.department.uuid),
                "name": obj.department.name,
                "short_name": obj.department.short_name,
                "type": "department",
            }
        elif obj.unit:
            # CampusUnit does not have `short_name` field. Use attribute safely and
            # fall back to slug or None if not present. This prevents AttributeError
            # when an official is associated with a CampusUnit.
            short_name = getattr(obj.unit, "short_name", None) or getattr(obj.unit, "slug", None)
            return {
                "id": obj.unit.id,
                "uuid": str(obj.unit.uuid),
                "name": obj.unit.name,
                "short_name": short_name,
                "type": "unit",
            }
        return None

    def get_program(self, obj):
        if obj.program:
            return {
                "id": obj.program.id,
                "name": obj.program.name,
                "short_name": obj.program.short_name,
            }
        return None

    def get_unit(self, obj):
        """Return unit info separately for clarity."""
        if obj.unit:
            short_name = getattr(obj.unit, "short_name", None) or getattr(obj.unit, "slug", None)
            return {
                "id": obj.unit.id,
                "uuid": str(obj.unit.uuid),
                "name": obj.unit.name,
                "short_name": short_name,
            }
        return None
    
    def get_fields(self):
        """Conditionally remove phone_number for public/non-CMS requests.

        Phone numbers are sensitive for public consumption. Include them only when:
        - request.user is staff or superuser, OR
        - request has query param `module=cms`, OR
        - serializer context contains `include_phone` True (allows callers to opt-in)
        """
        fields = super().get_fields()
        request = self.context.get("request")

        include_phone = False
        if self.context.get("include_phone"):
            include_phone = True
        elif request is not None:
            try:
                user = getattr(request, "user", None)
                if user and (getattr(user, "is_staff", False) or getattr(user, "is_superuser", False)):
                    include_phone = True
                elif request.query_params.get("module") == "cms" or request.query_params.get("source") == "cms":
                    include_phone = True
            except Exception:
                # be conservative and do not include phone if any error occurs
                include_phone = False

        if not include_phone:
            fields.pop("phone_number", None)

        return fields


class CampusKeyOfficialRetrieveSerializer(AbstractInfoRetrieveSerializer):
    designation = serializers.SlugRelatedField(
        read_only=True,
        slug_field="code",
    )
    designation_display = serializers.CharField(
        source="designation.title",
        read_only=True,
    )
    # Return department OR unit info
    department = serializers.SerializerMethodField()
    program = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = CampusKeyOfficial
        fields = [
            "id",
            "title_prefix",
            "full_name",
            "designation",
            "designation_display",
            "message",
            "photo",
            "email",
            "phone_number",
            "is_key_official",
            "department",
            "program",
            "unit",
            "display_order",
        ]

    def get_department(self, obj):
        """Return department info if exists, otherwise return unit info."""
        if obj.department:
            return {
                "id": obj.department.id,
                "uuid": str(obj.department.uuid),
                "name": obj.department.name,
                "short_name": obj.department.short_name,
                "email": obj.department.email,
                "type": "department",
            }
        elif obj.unit:
            short_name = getattr(obj.unit, "short_name", None) or getattr(obj.unit, "slug", None)
            email = getattr(obj.unit, "email", None) or getattr(obj.unit, "contact_email", None)
            return {
                "id": obj.unit.id,
                "uuid": str(obj.unit.uuid),
                "name": obj.unit.name,
                "short_name": short_name,
                "email": email,
                "type": "unit",
            }
        return None

    def get_unit(self, obj):
        """Return unit info separately."""
        if obj.unit:
            short_name = getattr(obj.unit, "short_name", None) or getattr(obj.unit, "slug", None)
            email = getattr(obj.unit, "email", None) or getattr(obj.unit, "contact_email", None)
            return {
                "id": obj.unit.id,
                "uuid": str(obj.unit.uuid),
                "name": obj.unit.name,
                "short_name": short_name,
                "email": email,
            }
        return None

    def get_program(self, obj):
        if obj.program:
            return {
                "id": obj.program.id,
                "name": obj.program.name,
                "short_name": obj.program.short_name,
            }
        return None

    def get_fields(self):
        """Apply same conditional phone hiding for retrieve serializer."""
        fields = super().get_fields()
        request = self.context.get("request")

        include_phone = False
        if self.context.get("include_phone"):
            include_phone = True
        elif request is not None:
            try:
                user = getattr(request, "user", None)
                if user and (getattr(user, "is_staff", False) or getattr(user, "is_superuser", False)):
                    include_phone = True
                elif request.query_params.get("module") == "cms" or request.query_params.get("source") == "cms":
                    include_phone = True
            except Exception:
                include_phone = False

        if not include_phone:
            fields.pop("phone_number", None)

        return fields


class CampusKeyOfficialCreateSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(
        allow_null=True,
        validators=[validate_photo_thumbnail],
    )
    designation = serializers.SlugRelatedField(
        slug_field="code",
        queryset=CampusStaffDesignation.objects.filter(is_active=True),
    )
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
        allow_null=True,
        required=False,
    )
    program = serializers.IntegerField(
        allow_null=True,
        required=False,
    )
    unit = serializers.PrimaryKeyRelatedField(
        queryset=CampusUnit.objects.filter(is_active=True),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = CampusKeyOfficial
        fields = [
            "title_prefix",
            "full_name",
            "designation",
            "photo",
            "email",
            "message",
            "phone_number",
            "is_key_official",
            "is_active",
            "department",
            "program",
            "unit",
            "display_order",
        ]

    def validate_program(self, value):
        if value is not None:
            from src.department.models import AcademicProgram

            try:
                return AcademicProgram.objects.get(id=value, is_active=True)
            except AcademicProgram.DoesNotExist:
                raise serializers.ValidationError("Invalid program ID.")
        return None

    def validate(self, attrs):
        program = attrs.get("program")
        department = attrs.get("department")
        unit = attrs.get("unit")

        # Ensure only one of department or unit is provided
        if department and unit:
            raise serializers.ValidationError(
                "Cannot assign both department and unit. Please provide only one.",
            )

        if program and department and program.department != department:
            raise serializers.ValidationError(
                {"program": "Program must belong to the selected department."},
            )

        # Program can only be assigned with department, not unit
        if program and not department:
            raise serializers.ValidationError(
                {
                    "program": "Program can only be assigned when a department is selected.",
                },
            )

        return attrs

    def create(self, validated_data):
        created_by = get_user_by_context(self.context)
        validated_data["created_by"] = created_by
        validated_data["full_name"] = validated_data.pop("full_name").title()

        return CampusKeyOfficial.objects.create(**validated_data)

    def to_representation(self, instance):
        return {"message": CAMPUS_KEY_OFFICIAL_CREATE_SUCCESS}


class CampusKeyOfficialPatchSerializer(serializers.ModelSerializer):
    designation = serializers.SlugRelatedField(
        slug_field="code",
        queryset=CampusStaffDesignation.objects.all(),
        required=False,
    )
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
        allow_null=True,
        required=False,
    )
    program = serializers.IntegerField(
        allow_null=True,
        required=False,
    )
    unit = serializers.PrimaryKeyRelatedField(
        queryset=CampusUnit.objects.filter(is_active=True),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = CampusKeyOfficial
        fields = [
            "title_prefix",
            "full_name",
            "designation",
            "photo",
            "message",
            "email",
            "phone_number",
            "is_key_official",
            "is_active",
            "department",
            "program",
            "unit",
            "display_order",
        ]

    def validate_program(self, value):
        if value is not None:
            from src.department.models import AcademicProgram

            try:
                return AcademicProgram.objects.get(id=value, is_active=True)
            except AcademicProgram.DoesNotExist:
                raise serializers.ValidationError("Invalid program ID.")
        return None

    def validate(self, attrs):
        program = attrs.get("program")
        department = attrs.get("department")
        unit = attrs.get("unit")

        # If values not provided in attrs, use existing values from instance
        if program is None and "program" not in attrs:
            program = getattr(self.instance, "program", None)
        if department is None and "department" not in attrs:
            department = getattr(self.instance, "department", None)
        if unit is None and "unit" not in attrs:
            unit = getattr(self.instance, "unit", None)

        # Ensure only one of department or unit is provided
        if department and unit:
            raise serializers.ValidationError(
                "Cannot assign both department and unit. Please provide only one.",
            )

        if program and department and program.department != department:
            raise serializers.ValidationError(
                {"program": "Program must belong to the selected department."},
            )

        # Program can only be assigned with department, not unit
        if program and not department:
            raise serializers.ValidationError(
                {
                    "program": "Program can only be assigned when a department is selected.",
                },
            )

        return attrs

    def update(self, instance: CampusKeyOfficial, validated_data):
        updated_by = get_user_by_context(self.context)

        if "full_name" in validated_data:
            validated_data["full_name"] = validated_data.pop("full_name").title()

        # Handle the photo
        if "photo" in validated_data:
            if instance.photo and default_storage.exists(instance.photo.name):
                default_storage.delete(instance.photo.name)

            instance.photo = validated_data.pop("photo", None)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.updated_by = updated_by
        instance.save()
        return instance


class CampusStaffDesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusStaffDesignation
        fields = [
            "id",
            "code",
            "title",
            "description",
            "is_active",
        ]

    # Use default representation so the viewset returns the actual designation
    # objects (id, code, title, description, is_active). Previously this
    # incorrectly returned a success message which prevented the frontend
    # from receiving selectable designation items.



# Campus Feedback Serializers
# ------------------------------------------------------------------------------------------------


class CampusFeedbackListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusFeedback
        fields = [
            "id",
            "full_name",
            "roll_number",
            "email",
            "message",
            "is_resolved",
            "created_at",
        ]


class CampusFeedbackResolveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusFeedback
        fields = ["is_resolved"]


# Campus Downloads Serializers
# ------------------------------------------------------------------------------------------------------


class CampusDownloadListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusDownload
        fields = ["id", "title", "file", "description", "is_active"]


class CampusDownloadRetrieveSerializer(AbstractInfoRetrieveSerializer):
    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = CampusDownload
        fields = ["id", "title", "file", "description"]
        fields += AbstractInfoRetrieveSerializer.Meta.fields


class CampusDownloadCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(validators=[validate_campus_download_file])

    class Meta:
        model = CampusDownload
        fields = ["title", "file", "description"]

    def create(self, validated_data):
        current_user = get_user_by_context(self.context)

        # Sanitize text fields
        validated_data["title"] = validated_data["title"].strip()
        validated_data["created_by"] = current_user

        return CampusDownload.objects.create(**validated_data)

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": CAMPUS_DOWNLOAD_CREATED_SUCCESS}


class CampusDownloadPatchSerializer(FileHandlingMixin, serializers.ModelSerializer):
    file = serializers.FileField(
        validators=[validate_campus_download_file],
        required=False,
    )

    class Meta:
        model = CampusDownload
        fields = ["title", "file", "description", "is_active"]

    def update(self, instance, validated_data):
        current_user = get_user_by_context(self.context)

        self.handle_file_update(instance, validated_data, "file")

        # Sanitize fields only if present
        title = validated_data.pop("title", None)
        if title is not None:
            instance.title = title.strip()

        description = validated_data.pop("description", None)
        if description is not None:
            instance.description = description.strip()

        if "is_active" in validated_data:
            instance.is_active = validated_data["is_active"]

        instance.updated_by = current_user
        instance.save()

        return instance

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": CAMPUS_DOWNLOAD_UPDATED_SUCCESS}


# Campus Reports Serializers
# ------------------------------------------------------------------------------------------------------


class FiscalSessionForCampusReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiscalSessionBS
        fields = ["id", "session_full", "session_short"]


class CampusReportListSerializer(serializers.ModelSerializer):
    fiscal_session = FiscalSessionForCampusReportSerializer()

    class Meta:
        model = CampusReport
        fields = [
            "id",
            "report_type",
            "fiscal_session",
            "published_date",
            "file",
            "is_active",
        ]


class CampusReportRetrieveSerializer(AbstractInfoRetrieveSerializer):
    fiscal_session = FiscalSessionForCampusReportSerializer()

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = CampusReport
        fields = [
            "id",
            "report_type",
            "fiscal_session",
            "published_date",
            "file",
        ]
        fields += AbstractInfoRetrieveSerializer.Meta.fields


class CampusReportCreateSerializer(serializers.ModelSerializer):
    fiscal_session = serializers.PrimaryKeyRelatedField(
        queryset=FiscalSessionBS.objects.filter(is_active=True),
    )

    class Meta:
        model = CampusReport
        fields = ["report_type", "fiscal_session", "published_date", "file"]

    def create(self, validated_data):
        current_user = get_user_by_context(self.context)
        validated_data["created_by"] = current_user
        return CampusReport.objects.create(**validated_data)

    def to_representation(self, instance):
        return {"message": CAMPUS_REPORT_CREATED_SUCCESS}


class CampusReportPatchSerializer(FileHandlingMixin, serializers.ModelSerializer):
    fiscal_session = serializers.PrimaryKeyRelatedField(
        queryset=FiscalSessionBS.objects.filter(is_active=True),
        required=False,
    )

    class Meta:
        model = CampusReport
        fields = [
            "report_type",
            "fiscal_session",
            "published_date",
            "file",
            "is_active",
        ]

    def update(self, instance, validated_data):
        current_user = get_user_by_context(self.context)

        self.handle_file_update(instance, validated_data, "file")

        for key, val in validated_data.items():
            setattr(instance, key, val)

        instance.updated_by = current_user
        instance.save()
        return instance

    def to_representation(self, instance):
        return {"message": CAMPUS_REPORT_UPDATED_SUCCESS}


# Campus Reports Serializers
# ------------------------------------------------------------------------------------------------------


class AcademicCalendarListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicCalendar
        fields = ["id", "program_type", "start_year", "end_year", "file", "is_active"]


class AcademicCalendarRetrieveSerializer(AbstractInfoRetrieveSerializer):
    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = AcademicCalendar
        fields = [
            "id",
            "program_type",
            "start_year",
            "end_year",
            "file",
        ]

        fields += AbstractInfoRetrieveSerializer.Meta.fields


class AcademicCalendarCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicCalendar
        fields = ["program_type", "start_year", "end_year", "file"]

    def validate(self, attrs):
        start = attrs.get("start_year")
        end = attrs.get("end_year")

        if start >= end:
            raise serializers.ValidationError({"end_year": YEAR_ORDER_ERROR})

        return attrs

    def create(self, validated_data):
        current_user = get_user_by_context(self.context)
        validated_data["created_by"] = current_user
        return AcademicCalendar.objects.create(**validated_data)

    def to_representation(self, instance):
        return {"message": ACADEMIC_CALENDER_CREATED_SUCCESS}


class AcademicCalendarPatchSerializer(FileHandlingMixin, serializers.ModelSerializer):
    class Meta:
        model = AcademicCalendar
        fields = ["program_type", "start_year", "end_year", "file", "is_active"]

    def validate(self, attrs):
        start = attrs.get("start_year", self.instance.start_year)
        end = attrs.get("end_year", self.instance.end_year)

        if start >= end:
            raise serializers.ValidationError({"end_year": YEAR_ORDER_ERROR})

        return attrs

    def update(self, instance, validated_data):
        current_user = get_user_by_context(self.context)

        self.handle_file_update(instance, validated_data, "file")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.updated_by = current_user
        instance.save()
        return instance

    def to_representation(self, instance):
        return {"message": ACADEMIC_CALENDER_UPDATED_SUCCESS}


# Campus Events Serializers
# ------------------------------------------------------------------------------------------------------


class CampusUnionListForOtherSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusUnion
        fields = ["id", "uuid", "name", "thumbnail"]

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": CAMPUS_EVENT_UPDATED_SUCCESS}


# Campus Union Serializers
# ------------------------------------------------------------------------------------------------------


class CampusUnionMemberListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusUnionMember
        fields = ["id", "full_name", "designation", "photo", "is_active"]


class CampusUnionListSerializer(serializers.ModelSerializer):
    department = DepartmentSummarySerializer(read_only=True)

    class Meta:
        model = CampusUnion
        fields = [
            "id",
            "name",
            "short_description",
            "thumbnail",
            "is_active",
            "department",
        ]


class CampusUnionRetrieveSerializer(AbstractInfoRetrieveSerializer):
    members = CampusUnionMemberListSerializer(many=True)
    department = DepartmentSummarySerializer(read_only=True)

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = CampusUnion
        fields = [
            "id",
            "name",
            "short_description",
            "thumbnail",
            "website_url",
            "detailed_description",
            "department",
            "members",
        ]

        fields += AbstractInfoRetrieveSerializer.Meta.fields


class CampusUnionMemberCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusUnionMember
        fields = ["full_name", "designation", "photo"]


class CampusUnionCreateSerializer(serializers.ModelSerializer):
    members = CampusUnionMemberCreateSerializer(many=True, allow_null=True)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
        allow_null=True,
        required=False,
    )
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
        required=False,
    )

    class Meta:
        model = CampusUnion
        fields = [
            "name",
            "short_description",
            "thumbnail",
            "detailed_description",
            "website_url",
            "members",
            "department",
        ]

    def create(self, validated_data):
        current_user = get_user_by_context(self.context)
        members_data = validated_data.pop("members", [])

        validated_data["name"] = validated_data["name"].strip()
        validated_data["created_by"] = current_user
        union = CampusUnion.objects.create(**validated_data)

        for member_data in members_data:
            CampusUnionMember.objects.create(
                union=union,
                **member_data,
                created_by=current_user,
            )

        return union

    def to_representation(self, instance):
        return {"message": CAMPUS_UNION_CREATED_SUCCESS}


class CampusUnionMemberPatchSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=CampusUnionMember.objects.filter(is_archived=False),
        required=False,
    )

    class Meta:
        model = CampusUnionMember
        fields = ["id", "full_name", "designation", "photo", "is_active"]


class CampusUnionPatchSerializer(FileHandlingMixin, serializers.ModelSerializer):
    members = CampusUnionMemberPatchSerializer(many=True, required=False)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = CampusUnion
        fields = [
            "name",
            "short_description",
            "thumbnail",
            "detailed_description",
            "website_url",
            "members",
            "department",
            "is_active",
        ]

    def update(self, instance, validated_data):
        current_user = get_user_by_context(self.context)
        union_members = validated_data.pop("members", [])

        self.handle_file_update(instance, validated_data, "thumbnail")

        name = validated_data.pop("name", None)
        if name is not None:
            instance.name = name.strip()

        for k, v in validated_data.items():
            setattr(instance, k, v)

        # Handle union members
        for union_member_data in union_members:
            if "id" in union_member_data:
                obj = union_member_data.pop("id")
                union_member_data["updated_by"] = current_user

                for key, val in union_member_data.items():
                    setattr(obj, key, val)
                obj.save()
            else:
                union_member_data["union"] = instance
                union_member_data["created_by"] = current_user
                CampusUnionMember.objects.create(**union_member_data)

        instance.updated_by = current_user
        instance.save()
        return instance

    def to_representation(self, instance):
        return {"message": CAMPUS_UNION_UPDATED_SUCCESS}


# Campus Section Serializers
# ------------------------------------------------------------------------------------------------------


class CampusSectionListSerializer(serializers.ModelSerializer):
    officials = CampusKeyOfficialListSerializer(
        source="members",
        many=True,
        read_only=True,
    )
    department_head_detail = CampusKeyOfficialListSerializer(
        source="department_head",
        read_only=True,
    )

    class Meta:
        model = CampusSection
        fields = [
            "id",
            "name",
            "slug",
            "short_description",
            "thumbnail",
            "display_order",
            "designations",
            "officials",
            "department_head",
            "department_head_detail",
            "is_active",
        ]


class CampusSectionRetrieveSerializer(AbstractInfoRetrieveSerializer):
    officials = CampusKeyOfficialListSerializer(
        source="members",
        many=True,
        read_only=True,
    )
    department_head_detail = CampusKeyOfficialListSerializer(
        source="department_head",
        read_only=True,
    )

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = CampusSection
        fields = [
            "id",
            "name",
            "slug",
            "short_description",
            "detailed_description",
            "objectives",
            "achievements",
            "thumbnail",
            "hero_image",
            "location",
            "contact_email",
            "contact_phone",
            "display_order",
            "designations",
            "officials",
            "members",
            "department_head",
            "department_head_detail",
        ]

        fields += AbstractInfoRetrieveSerializer.Meta.fields


class CampusSectionCreateSerializer(serializers.ModelSerializer):
    designations = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
    )
    members = serializers.PrimaryKeyRelatedField(
        queryset=CampusKeyOfficial.objects.filter(is_active=True, is_key_official=True),
        many=True,
        required=False,
        allow_empty=True,
    )
    department_head = serializers.PrimaryKeyRelatedField(
        queryset=CampusKeyOfficial.objects.filter(is_active=True, is_key_official=True),
        allow_null=True,
        required=False,
    )
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
        required=False,
    )
    hero_image = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
        required=False,
    )

    class Meta:
        model = CampusSection
        fields = [
            "name",
            "slug",
            "short_description",
            "detailed_description",
            "objectives",
            "achievements",
            "thumbnail",
            "hero_image",
            "location",
            "contact_email",
            "contact_phone",
            "display_order",
            "designations",
            "members",
            "department_head",
            "is_active",
        ]

    def create(self, validated_data):
        current_user = get_user_by_context(self.context)
        designations = validated_data.pop("designations", [])
        members = validated_data.pop("members", [])
        department_head = validated_data.get("department_head")
        slug = validated_data.get("slug")
        if not slug:
            validated_data["slug"] = slugify(validated_data["name"])
        else:
            validated_data["slug"] = slugify(slug)

        validated_data["designations"] = list(dict.fromkeys(designations))
        validated_data["created_by"] = current_user
        members_list = list(members)
        if department_head and department_head not in members_list:
            members_list.append(department_head)

        instance = CampusSection.objects.create(**validated_data)
        if members_list:
            instance.members.set(members_list)

        self._sync_designations_from_members(instance, members_list)
        return instance

    def validate_designations(self, value):
        return _validate_designation_codes(value)

    @staticmethod
    def _sync_designations_from_members(instance, members_list):
        members = members_list or []
        designations = []
        for member in members:
            designation = getattr(member, "designation", None)
            designation_code = (
                designation.code if designation and designation.code else None
            )
            if designation_code and designation_code not in designations:
                designations.append(designation_code)

        head_designation = (
            instance.department_head.designation
            if instance.department_head and instance.department_head.designation
            else None
        )
        head_designation_code = (
            head_designation.code
            if head_designation and head_designation.code
            else None
        )
        if head_designation_code and head_designation_code not in designations:
            designations.append(head_designation_code)

        if not designations:
            return

        instance.designations = designations
        instance.save(update_fields=["designations"])

    def to_representation(self, instance):
        return {"message": CAMPUS_SECTION_CREATED_SUCCESS}


class CampusSectionPatchSerializer(FileHandlingMixin, serializers.ModelSerializer):
    designations = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
    )
    members = serializers.PrimaryKeyRelatedField(
        queryset=CampusKeyOfficial.objects.filter(is_active=True, is_key_official=True),
        many=True,
        required=False,
        allow_empty=True,
    )
    department_head = serializers.PrimaryKeyRelatedField(
        queryset=CampusKeyOfficial.objects.filter(is_active=True, is_key_official=True),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = CampusSection
        fields = [
            "name",
            "slug",
            "short_description",
            "detailed_description",
            "objectives",
            "achievements",
            "thumbnail",
            "hero_image",
            "location",
            "contact_email",
            "contact_phone",
            "display_order",
            "designations",
            "members",
            "department_head",
            "is_active",
        ]

    def update(self, instance, validated_data):
        current_user = get_user_by_context(self.context)
        designations = validated_data.pop("designations", None)
        members = validated_data.pop("members", None)
        head_changed = "department_head" in validated_data

        self.handle_file_update(instance, validated_data, "thumbnail")
        self.handle_file_update(instance, validated_data, "hero_image")

        name = validated_data.pop("name", None)
        if name is not None:
            instance.name = name.strip()

        slug = validated_data.pop("slug", None)
        if slug is not None:
            instance.slug = slugify(slug) or instance.slug

        for key, value in validated_data.items():
            setattr(instance, key, value)

        if designations is not None:
            instance.designations = list(dict.fromkeys(designations))
        if members is not None:
            members_list = list(members)
            department_head = validated_data.get(
                "department_head",
                instance.department_head,
            )
            if department_head and department_head not in members_list:
                members_list.append(department_head)
            instance.members.set(members_list)
            CampusSectionCreateSerializer._sync_designations_from_members(
                instance,
                members_list,
            )
        elif head_changed:
            CampusSectionCreateSerializer._sync_designations_from_members(
                instance,
                list(instance.members.all()),
            )

        instance.updated_by = current_user
        instance.save()

        return instance

    def to_representation(self, instance):
        return {"message": CAMPUS_SECTION_UPDATED_SUCCESS}


# Campus Unit Serializers
# ------------------------------------------------------------------------------------------------------


class CampusUnitListSerializer(serializers.ModelSerializer):
    officials = CampusKeyOfficialListSerializer(
        source="members",
        many=True,
        read_only=True,
    )
    department_head_detail = CampusKeyOfficialListSerializer(
        source="department_head",
        read_only=True,
    )

    class Meta:
        model = CampusUnit
        fields = [
            "id",
            "name",
            "slug",
            "short_description",
            "thumbnail",
            "display_order",
            "designations",
            "officials",
            "department_head",
            "department_head_detail",
            "is_active",
        ]


class CampusUnitRetrieveSerializer(AbstractInfoRetrieveSerializer):
    officials = CampusKeyOfficialListSerializer(
        source="members",
        many=True,
        read_only=True,
    )
    department_head_detail = CampusKeyOfficialListSerializer(
        source="department_head",
        read_only=True,
    )

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = CampusUnit
        fields = [
            "id",
            "name",
            "slug",
            "short_description",
            "detailed_description",
            "objectives",
            "achievements",
            "thumbnail",
            "hero_image",
            "location",
            "contact_email",
            "contact_phone",
            "display_order",
            "designations",
            "officials",
            "members",
            "department_head",
            "department_head_detail",
        ]

        fields += AbstractInfoRetrieveSerializer.Meta.fields


class CampusUnitCreateSerializer(serializers.ModelSerializer):
    designations = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
    )
    members = serializers.PrimaryKeyRelatedField(
        queryset=CampusKeyOfficial.objects.filter(is_active=True, is_key_official=True),
        many=True,
        required=False,
        allow_empty=True,
    )
    department_head = serializers.PrimaryKeyRelatedField(
        queryset=CampusKeyOfficial.objects.filter(is_active=True, is_key_official=True),
        allow_null=True,
        required=False,
    )
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
        required=False,
    )
    hero_image = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
        required=False,
    )

    class Meta:
        model = CampusUnit
        fields = [
            "name",
            "slug",
            "short_description",
            "detailed_description",
            "objectives",
            "achievements",
            "thumbnail",
            "hero_image",
            "location",
            "contact_email",
            "contact_phone",
            "display_order",
            "designations",
            "members",
            "department_head",
            "is_active",
        ]

    def create(self, validated_data):
        current_user = get_user_by_context(self.context)
        designations = validated_data.pop("designations", [])
        members = validated_data.pop("members", [])
        department_head = validated_data.get("department_head")
        slug = validated_data.get("slug")
        if not slug:
            validated_data["slug"] = slugify(validated_data["name"])
        else:
            validated_data["slug"] = slugify(slug)

        validated_data["designations"] = list(dict.fromkeys(designations))
        validated_data["created_by"] = current_user
        members_list = list(members)
        if department_head and department_head not in members_list:
            members_list.append(department_head)

        instance = CampusUnit.objects.create(**validated_data)
        if members_list:
            instance.members.set(members_list)

        self._sync_designations_from_members(instance, members_list)
        return instance

    def validate_designations(self, value):
        return _validate_designation_codes(value)

    @staticmethod
    def _sync_designations_from_members(instance, members_list):
        members = members_list or []
        designations = []
        for member in members:
            designation = getattr(member, "designation", None)
            designation_code = (
                designation.code if designation and designation.code else None
            )
            if designation_code and designation_code not in designations:
                designations.append(designation_code)

        head_designation = (
            instance.department_head.designation
            if instance.department_head and instance.department_head.designation
            else None
        )
        head_designation_code = (
            head_designation.code
            if head_designation and head_designation.code
            else None
        )
        if head_designation_code and head_designation_code not in designations:
            designations.append(head_designation_code)

        if not designations:
            return

        instance.designations = designations
        instance.save(update_fields=["designations"])

    def to_representation(self, instance):
        return {"message": CAMPUS_UNIT_CREATED_SUCCESS}


class CampusUnitPatchSerializer(FileHandlingMixin, serializers.ModelSerializer):
    designations = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
    )
    members = serializers.PrimaryKeyRelatedField(
        queryset=CampusKeyOfficial.objects.filter(is_active=True, is_key_official=True),
        many=True,
        required=False,
        allow_empty=True,
    )
    department_head = serializers.PrimaryKeyRelatedField(
        queryset=CampusKeyOfficial.objects.filter(is_active=True, is_key_official=True),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = CampusUnit
        fields = [
            "name",
            "slug",
            "short_description",
            "detailed_description",
            "objectives",
            "achievements",
            "thumbnail",
            "hero_image",
            "location",
            "contact_email",
            "contact_phone",
            "display_order",
            "designations",
            "members",
            "department_head",
            "is_active",
        ]

    def update(self, instance, validated_data):
        current_user = get_user_by_context(self.context)
        designations = validated_data.pop("designations", None)
        members = validated_data.pop("members", None)
        head_changed = "department_head" in validated_data

        self.handle_file_update(instance, validated_data, "thumbnail")
        self.handle_file_update(instance, validated_data, "hero_image")

        name = validated_data.pop("name", None)
        if name is not None:
            instance.name = name.strip()

        slug = validated_data.pop("slug", None)
        if slug is not None:
            instance.slug = slugify(slug) or instance.slug

        for key, value in validated_data.items():
            setattr(instance, key, value)

        if designations is not None:
            instance.designations = list(dict.fromkeys(designations))
        if members is not None:
            members_list = list(members)
            department_head = validated_data.get(
                "department_head",
                instance.department_head,
            )
            if department_head and department_head not in members_list:
                members_list.append(department_head)
            instance.members.set(members_list)
            CampusUnitCreateSerializer._sync_designations_from_members(
                instance,
                members_list,
            )
        elif head_changed:
            CampusUnitCreateSerializer._sync_designations_from_members(
                instance,
                list(instance.members.all()),
            )

        instance.updated_by = current_user
        instance.save()
        return instance

    def validate_designations(self, value):
        if value is None:
            return None
        return _validate_designation_codes(value)

    def validate_designations(self, value):
        if value is None:
            return None
        return _validate_designation_codes(value)

    def to_representation(self, instance):
        return {"message": CAMPUS_UNIT_UPDATED_SUCCESS}


# Research Facility Serializers
# ------------------------------------------------------------------------------------------------------


class ResearchFacilityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchFacility
        fields = [
            "id",
            "name",
            "slug",
            "short_description",
            "thumbnail",
            "display_order",
            "is_active",
        ]


class ResearchFacilityRetrieveSerializer(AbstractInfoRetrieveSerializer):
    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = ResearchFacility
        fields = [
            "id",
            "name",
            "slug",
            "short_description",
            "description",
            "objectives",
            "thumbnail",
            "display_order",
        ]
        fields += AbstractInfoRetrieveSerializer.Meta.fields


class ResearchFacilityCreateSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
        required=False,
    )

    class Meta:
        model = ResearchFacility
        fields = [
            "name",
            "slug",
            "short_description",
            "description",
            "objectives",
            "thumbnail",
            "display_order",
            "is_active",
        ]

    def create(self, validated_data):
        current_user = get_user_by_context(self.context)
        slug_value = validated_data.get("slug") or validated_data["name"]
        validated_data["slug"] = slugify(slug_value)
        validated_data["created_by"] = current_user
        return ResearchFacility.objects.create(**validated_data)

    def to_representation(self, instance):
        return {"message": RESEARCH_FACILITY_CREATED_SUCCESS}


class ResearchFacilityPatchSerializer(FileHandlingMixin, serializers.ModelSerializer):
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
        required=False,
    )

    class Meta:
        model = ResearchFacility
        fields = [
            "name",
            "slug",
            "short_description",
            "description",
            "objectives",
            "thumbnail",
            "display_order",
            "is_active",
        ]

    def update(self, instance, validated_data):
        current_user = get_user_by_context(self.context)
        slug_value = validated_data.pop("slug", None)
        name = validated_data.get("name")

        self.handle_file_update(instance, validated_data, "thumbnail")

        if slug_value:
            slugified = slugify(slug_value)
            if slugified:
                instance.slug = slugified
        elif name:
            slugified = slugify(name)
            if slugified:
                instance.slug = slugified

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.updated_by = current_user
        instance.save()
        return instance

    def to_representation(self, instance):
        return {"message": RESEARCH_FACILITY_UPDATED_SUCCESS}


# Student Club Serializers
# ------------------------------------------------------------------------------------------------------


class GlobalGallerySerializer(serializers.Serializer):
    uuid = serializers.CharField()
    image = serializers.CharField(allow_blank=True, allow_null=True)
    caption = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    source_type = serializers.CharField()
    source_identifier = serializers.CharField()
    source_name = serializers.CharField()
    source_context = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.DateTimeField()


class GlobalGalleryImageSerializer(serializers.ModelSerializer):
    source_type = serializers.SerializerMethodField()
    source_identifier = serializers.SerializerMethodField()
    source_name = serializers.SerializerMethodField()
    source_context = serializers.SerializerMethodField()

    class Meta:
        model = GlobalGalleryImage
        fields = [
            "id",
            "uuid",
            "image",
            "caption",
            "display_order",
            "is_active",
            "created_at",
            "source_type",
            "source_identifier",
            "source_name",
            "source_context",
            "source_title",
            "union",
            "club",
            "department",
            "unit",
            "section",
            "global_event",
        ]

    def _source_values(self, obj):
        return resolve_gallery_image_source(obj)

    def get_source_type(self, obj):
        return self._source_values(obj)[0]

    def get_source_identifier(self, obj):
        return self._source_values(obj)[1]

    def get_source_name(self, obj):
        return self._source_values(obj)[2]

    def get_source_context(self, obj):
        return self._source_values(obj)[3]


class GlobalGalleryImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()
    caption = serializers.CharField(required=False, allow_blank=True)
    display_order = serializers.IntegerField(required=False, min_value=1)


class GlobalGalleryImageCreateSerializer(serializers.Serializer):

    union = serializers.PrimaryKeyRelatedField(
        queryset=CampusUnion.objects.filter(is_active=True, is_archived=False),
        allow_null=True,
        required=False,
    )
    club = serializers.PrimaryKeyRelatedField(
        queryset=StudentClub.objects.filter(is_active=True, is_archived=False),
        allow_null=True,
        required=False,
    )
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True, is_archived=False),
        allow_null=True,
        required=False,
    )
    unit = serializers.PrimaryKeyRelatedField(
        queryset=CampusUnit.objects.filter(is_active=True, is_archived=False),
        allow_null=True,
        required=False,
    )
    section = serializers.PrimaryKeyRelatedField(
        queryset=CampusSection.objects.filter(is_active=True, is_archived=False),
        allow_null=True,
        required=False,
    )
    global_event = serializers.PrimaryKeyRelatedField(
        queryset=GlobalEvent.objects.filter(is_active=True, is_archived=False),
        allow_null=True,
        required=False,
    )
    source_title = serializers.CharField(required=False, allow_blank=True)
    source_context = serializers.CharField(required=False, allow_blank=True)
    source_type = serializers.ChoiceField(
        choices=GlobalGalleryImage.SourceType.choices,
        required=False,
    )
    is_active = serializers.BooleanField(default=True)
    images = GlobalGalleryImageUploadSerializer(many=True)

    def validate(self, attrs):
        relation_fields = {
            "union": attrs.get("union"),
            "club": attrs.get("club"),
            "department": attrs.get("department"),
            "unit": attrs.get("unit"),
            "section": attrs.get("section"),
            "global_event": attrs.get("global_event"),
        }
        populated = [name for name, value in relation_fields.items() if value]
        if len(populated) > 1:
            raise serializers.ValidationError(
                "You can only associate one source relation per upload.",
            )

        if not populated and not attrs.get("source_title"):
            raise serializers.ValidationError(
                {
                    "source_title": "Provide a source title when no relation is selected.",
                },
            )

        if not attrs.get("images"):
            raise serializers.ValidationError(
                {"images": "Upload at least one gallery image."},
            )

        current_user = get_user_by_context(self.context)
        is_union_user = getattr(current_user, "is_union_member", None)
        if is_union_user and current_user.is_union_member():
            union = getattr(current_user, "union", None)
            if union is None:
                raise serializers.ValidationError(
                    {"union": "Union account is not linked to a union."},
                )

            if not populated:
                attrs["union"] = union
                populated = ["union"]
            else:
                relation_name = populated[0]
                if relation_name == "union":
                    submitted_union = attrs.get("union")
                    if submitted_union and submitted_union.pk != union.pk:
                        raise serializers.ValidationError(
                            {"union": "Union accounts can only select their own union."},
                        )
                    attrs["union"] = union
                elif relation_name == "global_event":
                    event = attrs.get("global_event")
                    if event and not event.unions.filter(pk=union.pk).exists():
                        raise serializers.ValidationError(
                            {"global_event": "Selected event is not associated with your union."},
                        )
                else:
                    raise serializers.ValidationError(
                        {
                            relation_name: "Union accounts cannot associate gallery items with this relation.",
                        },
                    )

        attrs["resolved_source_type"] = self._resolve_source_type(attrs, populated)
        attrs["resolved_relation"] = populated[0] if populated else None
        return attrs

    def _resolve_source_type(self, attrs, populated_relations):
        if populated_relations:
            relation_name = populated_relations[0]
            if relation_name == "campus_event":
                event = attrs.get("campus_event")
                if event and getattr(event, "union", None):
                    return GlobalGalleryImage.SourceType.UNION_EVENT
                return GlobalGalleryImage.SourceType.CAMPUS_EVENT
            if relation_name == "student_club_event":
                return GlobalGalleryImage.SourceType.CLUB_EVENT

            if relation_name == "global_event":
                return GlobalGalleryImage.SourceType.GLOBAL_EVENT
            if relation_name == "union":
                return GlobalGalleryImage.SourceType.UNION_GALLERY
            if relation_name == "club":
                return GlobalGalleryImage.SourceType.CLUB_GALLERY
            if relation_name == "department":
                return GlobalGalleryImage.SourceType.DEPARTMENT_GALLERY
            if relation_name == "unit":
                return GlobalGalleryImage.SourceType.UNIT_GALLERY
            if relation_name == "section":
                return GlobalGalleryImage.SourceType.SECTION_GALLERY

        return attrs.get("source_type", GlobalGalleryImage.SourceType.COLLEGE)

    def create(self, validated_data):
        current_user = get_user_by_context(self.context)
        images_data = validated_data.pop("images", [])
        resolved_type = validated_data.pop("resolved_source_type")
        resolved_relation = validated_data.pop("resolved_relation")
        relation_payload = {
            field: validated_data.get(field)
            for field in [
                "union",
                "club",
                "department",
                "unit",
                "section",
                "global_event",
            ]
        }
        source_title = validated_data.get("source_title", "").strip()
        source_context = validated_data.get("source_context", "").strip()

        created_images = []
        for idx, image_data in enumerate(images_data, start=1):
            image_kwargs = {
                "created_by": current_user,
                "source_type": resolved_type,
                "source_title": source_title,
                "source_context": source_context,
                "is_active": validated_data.get("is_active", True),
                "caption": image_data.get("caption", "").strip(),
                "display_order": image_data.get("display_order") or idx,
            }
            if resolved_relation:
                image_kwargs[resolved_relation] = relation_payload[resolved_relation]
            if getattr(current_user, "is_union_member", None) and current_user.is_union_member():
                union = getattr(current_user, "union", None)
                if union:
                    image_kwargs["union"] = union
            image_kwargs["image"] = image_data["image"]
            created_images.append(GlobalGalleryImage.objects.create(**image_kwargs))
        return created_images


class GlobalGalleryImageUpdateSerializer(
    FileHandlingMixin,
    serializers.ModelSerializer,
):
    class Meta:
        model = GlobalGalleryImage
        fields = [
            "image",
            "caption",
            "display_order",
            "is_active",
            "source_title",
            "source_context",
            # "campus_event",
            # "student_club_event",
            "union",
            "club",
            "department",
            "unit",
            "section",
            "global_event",
        ]

    def validate(self, attrs):
        current_user = get_user_by_context(self.context)
        is_union_user = getattr(current_user, "is_union_member", None)
        if is_union_user and current_user.is_union_member():
            union = getattr(current_user, "union", None)
            if union is None:
                raise serializers.ValidationError(
                    {"union": "Union account is not linked to a union."},
                )

            if "union" in attrs:
                submitted_union = attrs.get("union")
                if submitted_union and submitted_union.pk != union.pk:
                    raise serializers.ValidationError(
                        {"union": "Union accounts can only select their own union."},
                    )
                attrs["union"] = union
            else:
                attrs["union"] = union

            restricted_fields = ["club", "department", "unit", "section"]
            for field in restricted_fields:
                if field in attrs:
                    raise serializers.ValidationError(
                        {
                            field: "Union accounts cannot associate gallery items with this relation.",
                        },
                    )

            if "global_event" in attrs:
                event = attrs.get("global_event")
                if event and not event.unions.filter(pk=union.pk).exists():
                    raise serializers.ValidationError(
                        {"global_event": "Selected event is not associated with your union."},
                    )

        return attrs

    def update(self, instance, validated_data):
        current_user = get_user_by_context(self.context)
        self.handle_file_update(instance, validated_data, "image")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.updated_by = current_user
        instance.save()
        return instance


class StudentClubListForOtherSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClub
        fields = ["id", "uuid", "name"]


class GlobalEventListSerializer(serializers.ModelSerializer):
    unions = CampusUnionListForOtherSerializer(many=True, read_only=True)
    clubs = StudentClubListForOtherSerializer(many=True, read_only=True)
    departments = DepartmentSummarySerializer(many=True, read_only=True)

    class Meta:
        model = GlobalEvent
        fields = [
            "id",
            "uuid",
            "title",
            "event_type",
            "event_start_date",
            "event_end_date",
            "location",
            "registration_link",
            "thumbnail",
            "is_active",
            "is_approved_by_department",
            "is_approved_by_campus",
            "unions",
            "clubs",
            "departments",
            "created_at",
        ]


class GlobalEventRetrieveSerializer(AbstractInfoRetrieveSerializer):
    unions = CampusUnionListForOtherSerializer(many=True, read_only=True)
    clubs = StudentClubListForOtherSerializer(many=True, read_only=True)
    departments = DepartmentSummarySerializer(many=True, read_only=True)

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = GlobalEvent
        fields = [
            "id",
            "title",
            "description",
            "event_type",
            "event_start_date",
            "event_end_date",
            "location",
            "registration_link",
            "thumbnail",
            "is_approved_by_department",
            "is_approved_by_campus",
            "unions",
            "clubs",
            "departments",
        ]
        fields += AbstractInfoRetrieveSerializer.Meta.fields


class GlobalEventCreateSerializer(serializers.ModelSerializer):
    unions = serializers.PrimaryKeyRelatedField(
        queryset=CampusUnion.objects.filter(is_active=True),
        many=True,
        required=False,
    )
    clubs = serializers.PrimaryKeyRelatedField(
        queryset=StudentClub.objects.filter(is_active=True),
        many=True,
        required=False,
    )
    departments = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
        many=True,
        required=False,
    )
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
        required=False,
    )

    class Meta:
        model = GlobalEvent
        fields = [
            "title",
            "description",
            "event_type",
            "event_start_date",
            "event_end_date",
            "location",
            "registration_link",
            "thumbnail",
            "unions",
            "clubs",
            "departments",
            "is_active",
        ]

    def validate(self, attrs):
        start = attrs.get("event_start_date")
        end = attrs.get("event_end_date")
        if start and end and end < start:
            raise serializers.ValidationError({"event_end_date": EVENT_DATE_ERROR})

        current_user = get_user_by_context(self.context)
        
        # Handle union users
        if getattr(current_user, "is_union_member", None) and current_user.is_union_member():
            union = getattr(current_user, "union", None)
            if union is None:
                raise serializers.ValidationError({"unions": "Union account is not linked to a union."})

            submitted_unions = attrs.get("unions") or []
            if submitted_unions and any(union.pk != item.pk for item in submitted_unions):
                raise serializers.ValidationError({"unions": "Union accounts can only assign their own union."})

            # Always ensure the event is associated with the user's union
            attrs["unions"] = [union]
            
            # Clear departments and clubs for union users since they can't assign them
            attrs["departments"] = []
            attrs["clubs"] = []
            
        # Handle club users 
        elif hasattr(current_user, 'role') and current_user.role == 'CLUB':
            club = getattr(current_user, "club", None)
            if club is None:
                raise serializers.ValidationError({"clubs": "Club account is not linked to a club."})

            submitted_clubs = attrs.get("clubs") or []
            if submitted_clubs and any(club.pk != item.pk for item in submitted_clubs):
                raise serializers.ValidationError({"clubs": "Club accounts can only assign their own club."})

            # Always ensure the event is associated with the user's club
            attrs["clubs"] = [club]
            attrs["departments"] = [department]
            
            # Clear departments and unions for club users since they can't assign them
           
            attrs["unions"] = []
            
        # Handle department users
        elif hasattr(current_user, 'role') and current_user.role == 'DEPARTMENT':
            department = getattr(current_user, "department", None)
            if department is None:
                raise serializers.ValidationError({"departments": "Department account is not linked to a department."})

            submitted_departments = attrs.get("departments") or []
            if submitted_departments and any(department.pk != item.pk for item in submitted_departments):
                raise serializers.ValidationError({"departments": "Department accounts can only assign their own department."})

            # Always ensure the event is associated with the user's department
            attrs["departments"] = [department]
            
            # Department users can assign clubs but not unions
            # Clear unions for department users since they can't assign them
            attrs["unions"] = []

        return attrs

    def create(self, validated_data):
        unions = validated_data.pop("unions", [])
        clubs = validated_data.pop("clubs", [])
        departments = validated_data.pop("departments", [])
        current_user = get_user_by_context(self.context)

        validated_data["title"] = validated_data["title"].strip().title()
        if validated_data.get("description"):
            validated_data["description"] = validated_data["description"].strip()
        validated_data["created_by"] = current_user

        event = GlobalEvent.objects.create(**validated_data)
        event.unions.set(unions)
        event.clubs.set(clubs)
        event.departments.set(departments)
        return event

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": GLOBAL_EVENT_CREATED_SUCCESS}


class GlobalEventPatchSerializer(FileHandlingMixin, serializers.ModelSerializer):
    unions = serializers.PrimaryKeyRelatedField(
        queryset=CampusUnion.objects.filter(is_active=True),
        many=True,
        required=False,
    )
    clubs = serializers.PrimaryKeyRelatedField(
        queryset=StudentClub.objects.filter(is_active=True),
        many=True,
        required=False,
    )
    departments = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
        many=True,
        required=False,
    )
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
        required=False,
    )

    class Meta:
        model = GlobalEvent
        fields = [
            "title",
            "description",
            "event_type",
            "event_start_date",
            "event_end_date",
            "location",
            "registration_link",
            "thumbnail",
            "is_active",
            "unions",
            "clubs",
            "departments",
        ]

    def validate(self, attrs):
        start = attrs.get(
            "event_start_date",
            self.instance.event_start_date,
        )
        end = attrs.get("event_end_date", self.instance.event_end_date)
        if start and end and end < start:
            raise serializers.ValidationError({"event_end_date": EVENT_DATE_ERROR})

        current_user = get_user_by_context(self.context)
        if getattr(current_user, "is_union_member", None) and current_user.is_union_member():
            union = getattr(current_user, "union", None)
            if union is None:
                raise serializers.ValidationError({"unions": "Union account is not linked to a union."})

            submitted_unions = attrs.get("unions")
            if submitted_unions is not None and any(union.pk != item.pk for item in submitted_unions):
                raise serializers.ValidationError({"unions": "Union accounts can only assign their own union."})

            # Preserve association with the logged-in union
            attrs["unions"] = [union]

        return attrs

    def update(self, instance, validated_data):
        unions = validated_data.pop("unions", None)
        clubs = validated_data.pop("clubs", None)
        departments = validated_data.pop("departments", None)
        current_user = get_user_by_context(self.context)

        self.handle_file_update(instance, validated_data, "thumbnail")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if unions is not None:
            instance.unions.set(unions)
        if clubs is not None:
            instance.clubs.set(clubs)
        if departments is not None:
            instance.departments.set(departments)

        instance.updated_by = current_user
        instance.save()
        return instance

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": GLOBAL_EVENT_UPDATED_SUCCESS}


class StudentClubMemberListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClubMember
        fields = ["id", "full_name", "designation", "photo", "is_active"]


class StudentClubListSerializer(serializers.ModelSerializer):
    department = DepartmentSummarySerializer(read_only=True)

    class Meta:
        model = StudentClub
        fields = [
            "id",
            "name",
            "short_description",
            "thumbnail",
            "website_url",
            "is_active",
            "department",
        ]


class StudentClubRetrieveSerializer(AbstractInfoRetrieveSerializer):
    members = StudentClubMemberListSerializer(many=True)
    department = DepartmentSummarySerializer(read_only=True)

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = StudentClub
        fields = [
            "id",
            "name",
            "short_description",
            "thumbnail",
            "website_url",
            "detailed_description",
            "members",
            "department",
        ]

        fields += AbstractInfoRetrieveSerializer.Meta.fields


class StudentClubMemberCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClubMember
        fields = ["full_name", "designation", "photo"]


class StudentClubCreateSerializer(serializers.ModelSerializer):
    members = StudentClubMemberCreateSerializer(many=True, allow_null=True)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
        allow_null=True,
        required=False,
    )
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
        required=False,
    )

    class Meta:
        model = StudentClub
        fields = [
            "name",
            "short_description",
            "thumbnail",
            "detailed_description",
            "website_url",
            "members",
            "department",
        ]

    def create(self, validated_data):
        current_user = get_user_by_context(self.context)
        members_data = validated_data.pop("members", [])

        validated_data["name"] = validated_data["name"].strip()
        validated_data["created_by"] = current_user
        club = StudentClub.objects.create(**validated_data)

        for member_data in members_data:
            StudentClubMember.objects.create(
                club=club,
                **member_data,
                created_by=current_user,
            )

        return club

    def to_representation(self, instance):
        return {"message": CAMPUS_CLUB_CREATED_SUCCESS}


class StudentClubMemberPatchSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=StudentClubMember.objects.filter(is_archived=False),
        required=False,
    )

    class Meta:
        model = StudentClubMember
        fields = ["id", "full_name", "designation", "photo", "is_active"]


class StudentClubPatchSerializer(FileHandlingMixin, serializers.ModelSerializer):
    members = StudentClubMemberPatchSerializer(many=True, required=False)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
        allow_null=True,
        required=False,
    )
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
        required=False,
    )

    class Meta:
        model = StudentClub
        fields = [
            "name",
            "short_description",
            "thumbnail",
            "detailed_description",
            "website_url",
            "members",
            "department",
            "is_active",
        ]

    def update(self, instance, validated_data):
        current_user = get_user_by_context(self.context)
        club_members = validated_data.pop("members", [])

        self.handle_file_update(instance, validated_data, "thumbnail")

        name = validated_data.pop("name", None)
        if name is not None:
            instance.name = name.strip()

        for k, v in validated_data.items():
            setattr(instance, k, v)

        # Handle club members
        for club_member_data in club_members:
            if "id" in club_member_data:
                obj = club_member_data.pop("id")
                club_member_data["updated_by"] = current_user

                for key, val in club_member_data.items():
                    setattr(obj, key, val)
                obj.save()
            else:
                club_member_data["club"] = instance
                club_member_data["created_by"] = current_user
                StudentClubMember.objects.create(**club_member_data)

        instance.updated_by = current_user
        instance.save()
        return instance

    def to_representation(self, instance):
        return {"message": CAMPUS_CLUB_UPDATED_SUCCESS}
