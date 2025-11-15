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
    RESEARCH_FACILITY_CREATED_SUCCESS,
    RESEARCH_FACILITY_DELETED_SUCCESS,
    RESEARCH_FACILITY_NOT_FOUND,
    RESEARCH_FACILITY_UPDATED_SUCCESS,
    SOCIAL_MEDIA_ALREADY_EXISTS,
    STUDENT_CLUB_EVENT_CREATED_SUCCESS,
    STUDENT_CLUB_EVENT_UPDATED_SUCCESS,
    YEAR_ORDER_ERROR,
)
from .models import (
    AcademicCalendar,
    CampusDownload,
    CampusEvent,
    CampusEventGallery,
    CampusFeedback,
    CampusInfo,
    CampusKeyOfficial,
    CampusSection,
    CampusStaffDesignation,
    CampusUnit,
    ResearchFacility,
    CampusReport,
    CampusUnion,
    CampusUnionMember,
    SocialMediaLink,
    StudentClub,
    StudentClubEvent,
    StudentClubEventGallery,
    StudentClubMember,
    GlobalGalleryCollection,
    GlobalGalleryImage,
)


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
            "code", flat=True
        )
    )
    invalid_codes = sorted(
        {code for code in cleaned_codes if code not in existing_codes}
    )
    if invalid_codes:
        raise serializers.ValidationError(
            f"Invalid designation codes: {', '.join(invalid_codes)}"
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
                        {"message": SOCIAL_MEDIA_ALREADY_EXISTS}
                    )
            else:
                if media_ins.exists():
                    raise serializers.ValidationError(
                        {"message": SOCIAL_MEDIA_ALREADY_EXISTS}
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
        ]


class CampusKeyOfficialRetrieveSerializer(AbstractInfoRetrieveSerializer):
    designation = serializers.SlugRelatedField(
        read_only=True,
        slug_field="code",
    )
    designation_display = serializers.CharField(
        source="designation.title",
        read_only=True,
    )

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
        ]

        fields += AbstractInfoRetrieveSerializer.Meta.fields


class CampusKeyOfficialCreateSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(
        allow_null=True, validators=[validate_photo_thumbnail]
    )
    designation = serializers.SlugRelatedField(
        slug_field="code",
        queryset=CampusStaffDesignation.objects.filter(is_active=True),
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
        ]

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
        ]

    def update(self, instance: CampusKeyOfficial, validated_data):
        updated_by = get_user_by_context(self.context)
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
            "display_order",
            "is_active",
        ]

    def to_representation(self, instance):
        return {"message": CAMPUS_KEY_OFFICIAL_UPDATE_SUCCESS}


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
        start = attrs.get("start_year", getattr(self.instance, "start_year"))
        end = attrs.get("end_year", getattr(self.instance, "end_year"))

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


class CampusEventGalleryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusEventGallery
        fields = ["id", "image", "caption", "is_active"]


class CampusEventListSerializer(serializers.ModelSerializer):
    union = CampusUnionListForOtherSerializer(read_only=True)

    class Meta:
        model = CampusEvent
        fields = [
            "id",
            "title",
            "event_type",
            "event_start_date",
            "event_end_date",
            "thumbnail",
            "is_active",
            "union",
        ]


class CampusEventRetrieveSerializer(AbstractInfoRetrieveSerializer):
    gallery = CampusEventGalleryListSerializer(many=True, read_only=True)
    union = CampusUnionListForOtherSerializer(read_only=True)

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = CampusEvent
        fields = [
            "id",
            "title",
            "description_short",
            "description_detailed",
            "event_type",
            "event_start_date",
            "event_end_date",
            "thumbnail",
            "gallery",
            "union",
        ]
        fields += AbstractInfoRetrieveSerializer.Meta.fields


class CampusEventGalleryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusEventGallery
        fields = ["image", "caption"]


class CampusEventCreateSerializer(serializers.ModelSerializer):
    union = serializers.PrimaryKeyRelatedField(
        queryset=CampusUnion.objects.filter(is_active=True),
        allow_null=True,
        required=False,
    )
    gallery = CampusEventGalleryCreateSerializer(many=True, required=False)
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
    )

    class Meta:
        model = CampusEvent
        fields = [
            "title",
            "description_short",
            "description_detailed",
            "event_type",
            "event_start_date",
            "event_end_date",
            "thumbnail",
            "gallery",
            "union",
        ]

    def validate(self, attrs):
        start = attrs.get("event_start_date")
        end = attrs.get("event_end_date")
        if start and end and end < start:
            raise serializers.ValidationError({"event_end_date": EVENT_DATE_ERROR})
        return attrs

    def create(self, validated_data):
        gallery_data = validated_data.pop("gallery", [])
        current_user = get_user_by_context(self.context)

        validated_data["title"] = validated_data["title"].strip().title()
        validated_data["description_short"] = validated_data[
            "description_short"
        ].strip()
        validated_data["created_by"] = current_user

        event = CampusEvent.objects.create(**validated_data)

        for image_data in gallery_data:
            image_data["event"] = event
            image_data["created_by"] = current_user
            CampusEventGallery.objects.create(**image_data)

        return event

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": CAMPUS_EVENT_CREATED_SUCCESS}


class CampusEventGalleryPatchSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=CampusEventGallery.objects.filter(is_archived=False),
        required=False,
    )

    class Meta:
        model = CampusEventGallery
        fields = ["id", "image", "caption", "is_active"]


class CampusEventPatchSerializer(FileHandlingMixin, serializers.ModelSerializer):
    gallery = CampusEventGalleryPatchSerializer(many=True, required=False)
    union = serializers.PrimaryKeyRelatedField(
        queryset=CampusUnion.objects.filter(is_active=True),
        allow_null=True,
        required=False,
    )
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
        required=False,
    )

    class Meta:
        model = CampusEvent
        fields = [
            "title",
            "description_short",
            "description_detailed",
            "event_type",
            "event_start_date",
            "event_end_date",
            "thumbnail",
            "gallery",
            "is_active",
            "union",
        ]

    def validate(self, attrs):
        start = attrs.get("event_start_date")
        end = attrs.get("event_end_date")
        if start and end and end < start:
            raise serializers.ValidationError({"event_end_date": EVENT_DATE_ERROR})
        return attrs

    def update(self, instance, validated_data):
        gallery_data = validated_data.pop("gallery", [])
        current_user = get_user_by_context(self.context)

        self.handle_file_update(instance, validated_data, "thumbnail")

        # Update fields only if present
        if "title" in validated_data:
            validated_data["title"] = validated_data.pop("title").strip().title()

        for key, val in validated_data.items():
            setattr(instance, key, val)

        # Handle Event Gallery
        for gallery in gallery_data:
            obj = gallery.pop("id", None)
            if obj:
                gallery["updated_by"] = current_user

                for key, val in gallery.items():
                    setattr(obj, key, val)
                obj.save()
            else:
                gallery["event"] = instance
                gallery["created_by"] = current_user
                CampusEventGallery.objects.create(**gallery)

        instance.updated_by = current_user
        instance.save()

        return instance

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
        fields = ["id", "name", "short_description", "thumbnail", "is_active", "department"]


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
        source="members", many=True, read_only=True
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
        source="members", many=True, read_only=True
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
        queryset=CampusKeyOfficial.objects.filter(
            is_active=True, is_key_official=True
        ),
        many=True,
        required=False,
        allow_empty=True,
    )
    department_head = serializers.PrimaryKeyRelatedField(
        queryset=CampusKeyOfficial.objects.filter(
            is_active=True, is_key_official=True
        ),
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
            head_designation.code if head_designation and head_designation.code else None
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
        queryset=CampusKeyOfficial.objects.filter(
            is_active=True, is_key_official=True
        ),
        many=True,
        required=False,
        allow_empty=True,
    )
    department_head = serializers.PrimaryKeyRelatedField(
        queryset=CampusKeyOfficial.objects.filter(
            is_active=True, is_key_official=True
        ),
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
                "department_head", instance.department_head
            )
            if department_head and department_head not in members_list:
                members_list.append(department_head)
            instance.members.set(members_list)
            CampusSectionCreateSerializer._sync_designations_from_members(
                instance, members_list
            )
        elif head_changed:
            CampusSectionCreateSerializer._sync_designations_from_members(
                instance, list(instance.members.all())
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
        source="members", many=True, read_only=True
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
        source="members", many=True, read_only=True
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
        queryset=CampusKeyOfficial.objects.filter(
            is_active=True, is_key_official=True
        ),
        many=True,
        required=False,
        allow_empty=True,
    )
    department_head = serializers.PrimaryKeyRelatedField(
        queryset=CampusKeyOfficial.objects.filter(
            is_active=True, is_key_official=True
        ),
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
            head_designation.code if head_designation and head_designation.code else None
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
        queryset=CampusKeyOfficial.objects.filter(
            is_active=True, is_key_official=True
        ),
        many=True,
        required=False,
        allow_empty=True,
    )
    department_head = serializers.PrimaryKeyRelatedField(
        queryset=CampusKeyOfficial.objects.filter(
            is_active=True, is_key_official=True
        ),
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
                "department_head", instance.department_head
            )
            if department_head and department_head not in members_list:
                members_list.append(department_head)
            instance.members.set(members_list)
            CampusUnitCreateSerializer._sync_designations_from_members(
                instance, members_list
            )
        elif head_changed:
            CampusUnitCreateSerializer._sync_designations_from_members(
                instance, list(instance.members.all())
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
    id = serializers.IntegerField(required=False)

    class Meta:
        model = GlobalGalleryImage
        fields = ["id", "image", "caption", "display_order"]


class GlobalGalleryCollectionListSerializer(serializers.ModelSerializer):
    campus_event = serializers.SerializerMethodField()
    student_club_event = serializers.SerializerMethodField()
    department_event = serializers.SerializerMethodField()
    union = serializers.SerializerMethodField()
    club = serializers.SerializerMethodField()
    images = GlobalGalleryImageSerializer(many=True, read_only=True)
    department = DepartmentSummarySerializer(read_only=True)

    class Meta:
        model = GlobalGalleryCollection
        fields = [
            "uuid",
            "title",
            "description",
            "is_active",
            "campus_event",
            "student_club_event",
            "department_event",
            "union",
            "club",
            "department",
            "images",
            "created_at",
        ]

    def _serialize_entity(self, attr_name, obj):
        entity = getattr(obj, attr_name)
        if entity:
            name = getattr(entity, "name", getattr(entity, "title", ""))
            return {"uuid": str(entity.uuid), "name": name}
        return None

    def get_campus_event(self, obj):
        return self._serialize_entity("campus_event", obj)

    def get_student_club_event(self, obj):
        return self._serialize_entity("student_club_event", obj)

    def get_department_event(self, obj):
        return self._serialize_entity("department_event", obj)

    def get_union(self, obj):
        return self._serialize_entity("union", obj)

    def get_club(self, obj):
        return self._serialize_entity("club", obj)


class GlobalGalleryCollectionCreateSerializer(serializers.ModelSerializer):
    images = GlobalGalleryImageSerializer(many=True)

    class Meta:
        model = GlobalGalleryCollection
        fields = [
            "title",
            "description",
            "campus_event",
            "student_club_event",
            "department_event",
            "union",
            "club",
            "department",
            "is_active",
            "images",
        ]

    def create(self, validated_data):
        current_user = get_user_by_context(self.context)
        images_data = validated_data.pop("images", [])
        validated_data["created_by"] = current_user
        collection = GlobalGalleryCollection.objects.create(**validated_data)
        self._create_images(collection, images_data, current_user)
        return collection

    def _create_images(self, collection, images_data, user):
        for idx, image_data in enumerate(images_data, start=1):
            image_data.setdefault("display_order", idx)
            GlobalGalleryImage.objects.create(
                collection=collection,
                created_by=user,
                **image_data,
            )


class GlobalGalleryCollectionPatchSerializer(serializers.ModelSerializer):
    images = GlobalGalleryImageSerializer(many=True, required=False)

    class Meta:
        model = GlobalGalleryCollection
        fields = [
            "title",
            "description",
            "campus_event",
            "student_club_event",
            "department_event",
            "union",
            "club",
            "department",
            "is_active",
            "images",
        ]

    def update(self, instance, validated_data):
        current_user = get_user_by_context(self.context)
        images_data = validated_data.pop("images", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if images_data is not None:
            instance.images.all().delete()
            for idx, image_data in enumerate(images_data, start=1):
                image_data.setdefault("display_order", idx)
                GlobalGalleryImage.objects.create(
                    collection=instance,
                    created_by=current_user,
                    **image_data,
                )

        instance.updated_by = current_user
        instance.save()
        return instance

class StudentClubMemberListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClubMember
        fields = ["id", "full_name", "designation", "photo", "is_active"]


class StudentClubListSerializer(serializers.ModelSerializer):
    department = DepartmentSummarySerializer(read_only=True)

    class Meta:
        model = StudentClub
        fields = ["id", "name", "short_description", "thumbnail", "is_active", "department"]


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


class StudentClubListForOtherSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClub
        fields = ["id", "name"]


# Student Club Events Serializers
# ------------------------------------------------------------------------------------------------------


class StudentClubEventGalleryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClubEventGallery
        fields = ["id", "image", "caption", "is_active"]


class StudentClubEventListSerializer(serializers.ModelSerializer):
    club = StudentClubListForOtherSerializer()

    class Meta:
        model = StudentClubEvent
        fields = [
            "id",
            "title",
            "date",
            "thumbnail",
            "club",
            "is_active",
        ]


class StudentClubEventRetrieveSerializer(AbstractInfoRetrieveSerializer):
    club = StudentClubListForOtherSerializer()
    gallery = StudentClubEventGalleryListSerializer(many=True, read_only=True)

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = StudentClubEvent
        fields = [
            "id",
            "title",
            "description",
            "date",
            "thumbnail",
            "club",
            "gallery",
        ]
        fields += AbstractInfoRetrieveSerializer.Meta.fields


class StudentClubEventGalleryCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(validators=[validate_photo_thumbnail])

    class Meta:
        model = StudentClubEventGallery
        fields = ["image", "caption"]


class StudentClubEventCreateSerializer(serializers.ModelSerializer):
    club = serializers.PrimaryKeyRelatedField(
        queryset=StudentClub.objects.filter(is_active=True),
    )
    gallery = StudentClubEventGalleryCreateSerializer(many=True, required=False)
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
    )

    class Meta:
        model = StudentClubEvent
        fields = [
            "title",
            "description",
            "date",
            "thumbnail",
            "club",
            "gallery",
        ]

    def create(self, validated_data):
        gallery_data = validated_data.pop("gallery", [])
        current_user = get_user_by_context(self.context)

        validated_data["title"] = validated_data["title"].strip().title()
        validated_data["description"] = validated_data.get("description", "").strip()
        validated_data["created_by"] = current_user

        event = StudentClubEvent.objects.create(**validated_data)

        for image_data in gallery_data:
            image_data["event"] = event
            image_data["created_by"] = current_user
            StudentClubEventGallery.objects.create(**image_data)

        return event

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": STUDENT_CLUB_EVENT_CREATED_SUCCESS}


class StudentClubEventGalleryPatchSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=StudentClubEventGallery.objects.filter(is_archived=False),
        required=False,
    )
    image = serializers.ImageField(validators=[validate_photo_thumbnail])

    class Meta:
        model = StudentClubEventGallery
        fields = ["id", "image", "caption", "is_active"]


class StudentClubEventPatchSerializer(FileHandlingMixin, serializers.ModelSerializer):
    club = serializers.PrimaryKeyRelatedField(
        queryset=StudentClub.objects.filter(is_active=True),
        required=False,
    )
    gallery = StudentClubEventGalleryPatchSerializer(many=True, required=False)
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
        required=False,
    )

    class Meta:
        model = StudentClubEvent
        fields = [
            "title",
            "description",
            "date",
            "thumbnail",
            "club",
            "gallery",
            "is_active",
        ]

    def update(self, instance, validated_data):
        gallery_data = validated_data.pop("gallery", [])
        current_user = get_user_by_context(self.context)

        self.handle_file_update(instance, validated_data, "thumbnail")

        # Update fields only if present
        if "title" in validated_data:
            validated_data["title"] = validated_data.pop("title").strip().title()

        for key, val in validated_data.items():
            setattr(instance, key, val)

        # Handle Event Gallery
        for gallery in gallery_data:
            if "id" in gallery:
                obj = gallery.pop("id")
                gallery["updated_by"] = current_user

                for key, val in gallery.items():
                    setattr(obj, key, val)
                obj.save()
            else:
                gallery["event"] = instance
                gallery["created_by"] = current_user
                StudentClubEventGallery.objects.create(**gallery)

        instance.updated_by = current_user
        instance.save()

        return instance

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": STUDENT_CLUB_EVENT_UPDATED_SUCCESS}
