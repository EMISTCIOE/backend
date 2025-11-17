from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

# Project Imports
from src.core.models import FiscalSessionBS
from src.department.models import Department
from src.website.models import (
    AcademicCalendar,
    CampusDownload,
    CampusFeedback,
    CampusInfo,
    CampusKeyOfficial,
    CampusSection,
    CampusUnit,
    ResearchFacility,
    CampusReport,
    CampusUnion,
    CampusUnionMember,
    GlobalEvent,
    SocialMediaLink,
    StudentClub,
    StudentClubMember,
)
from src.website.public.messages import (
    FEEDBACK_FULL_NAME_REQUIRED,
    FEEDBACK_MESSAGE_TOO_SHORT,
)


class PublicDepartmentSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "uuid", "name"]


class PublicSocialMediaLinkForCampusInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaLink
        fields = ["uuid", "platform", "url"]


class PublicCampusInfoSerializer(serializers.ModelSerializer):
    social_links = serializers.SerializerMethodField()

    class Meta:
        model = CampusInfo
        fields = [
            "name",
            "phone_number",
            "email",
            "organization_chart",
            "location",
            "social_links",
        ]

    @extend_schema_field(PublicSocialMediaLinkForCampusInfoSerializer(many=True))
    def get_social_links(self, obj):
        return PublicSocialMediaLinkForCampusInfoSerializer(
            SocialMediaLink.objects.filter(is_active=True),
            many=True,
        ).data


class PublicCampusDownloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusDownload
        fields = ["uuid", "title", "description", "file", "created_at"]


class PublicCampusUnionCompactSerializer(serializers.ModelSerializer):
    department = PublicDepartmentSummarySerializer(read_only=True)

    class Meta:
        model = CampusUnion
        fields = ["uuid", "name", "thumbnail", "department"]


class PublicCampusKeyOfficialSerializer(serializers.ModelSerializer):
    designation = serializers.SlugRelatedField(read_only=True, slug_field="code")
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
            "title_prefix",
            "title_prefix_display",
            "full_name",
            "designation",
            "designation_display",
            "message",
            "photo",
            "email",
            "phone_number",
            "is_key_official",
        ]


class PublicCampusFeedbackSerializer(serializers.ModelSerializer):
    MIN_MESSAGE_LENGTH = 10

    class Meta:
        model = CampusFeedback
        fields = [
            "full_name",
            "roll_number",
            "email",
            "message",
        ]

    def validate_full_name(self, value):
        cleaned_value = value.strip()
        if not cleaned_value:
            raise serializers.ValidationError(FEEDBACK_FULL_NAME_REQUIRED)
        return cleaned_value

    def validate_message(self, value):
        cleaned_value = value.strip()
        if len(cleaned_value) < self.MIN_MESSAGE_LENGTH:
            raise serializers.ValidationError(
                FEEDBACK_MESSAGE_TOO_SHORT.format(min_length=self.MIN_MESSAGE_LENGTH),
            )
        return cleaned_value

    def create(self, validated_data):
        validated_data["is_resolved"] = False
        return super().create(validated_data)


class PublicAcademicCalendarListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicCalendar
        fields = ["uuid", "program_type", "start_year", "end_year", "file"]


class PublicFiscalSessionForCampusReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiscalSessionBS
        fields = ["uuid", "session_full", "session_short"]


class PublicCampusReportListSerializer(serializers.ModelSerializer):
    fiscal_session = PublicFiscalSessionForCampusReportSerializer()

    class Meta:
        model = CampusReport
        fields = ["uuid", "report_type", "fiscal_session", "published_date", "file"]


# Campus Unions and Clubs Serializers
# ----------------------------------------------------------------------------------------------------


class PublicCampusUnionMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusUnionMember
        fields = ["uuid", "full_name", "designation", "photo"]


class PublicCampusUnionListSerializer(serializers.ModelSerializer):
    department = PublicDepartmentSummarySerializer(read_only=True)

    class Meta:
        model = CampusUnion
        fields = ["uuid", "name", "thumbnail", "short_description", "department"]


class PublicCampusUnionRetrieveSerializer(serializers.ModelSerializer):
    members = PublicCampusUnionMemberSerializer(many=True, read_only=True)
    department = PublicDepartmentSummarySerializer(read_only=True)

    class Meta:
        model = CampusUnion
        fields = [
            "uuid",
            "thumbnail",
            "name",
            "short_description",
            "website_url",
            "detailed_description",
            "members",
            "department",
        ]


class PublicStudentClubMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClubMember
        fields = ["uuid", "full_name", "designation", "photo"]


class PublicStudentClubListSerializer(serializers.ModelSerializer):
    department = PublicDepartmentSummarySerializer(read_only=True)

    class Meta:
        model = StudentClub
        fields = [
            "uuid",
            "name",
            "short_description",
            "thumbnail",
            "website_url",
            "department",
        ]


class PublicStudentClubRetrieveSerializer(serializers.ModelSerializer):
    members = PublicStudentClubMemberSerializer(many=True, read_only=True)
    department = PublicDepartmentSummarySerializer(read_only=True)

    class Meta:
        model = StudentClub
        fields = [
            "uuid",
            "name",
            "short_description",
            "detailed_description",
            "website_url",
            "thumbnail",
            "members",
            "department",
        ]


class PublicCampusSectionListSerializer(serializers.ModelSerializer):
    officials = PublicCampusKeyOfficialSerializer(
        source="members", many=True, read_only=True
    )
    department_head = PublicCampusKeyOfficialSerializer(
        read_only=True,
    )

    class Meta:
        model = CampusSection
        fields = [
            "uuid",
            "name",
            "slug",
            "short_description",
            "thumbnail",
            "display_order",
            "officials",
            "department_head",
        ]


class PublicCampusSectionRetrieveSerializer(serializers.ModelSerializer):
    officials = PublicCampusKeyOfficialSerializer(
        source="members", many=True, read_only=True
    )
    department_head = PublicCampusKeyOfficialSerializer(
        read_only=True,
    )

    class Meta:
        model = CampusSection
        fields = [
            "uuid",
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
            "officials",
            "department_head",
        ]


class PublicCampusUnitListSerializer(serializers.ModelSerializer):
    officials = PublicCampusKeyOfficialSerializer(
        source="members", many=True, read_only=True
    )
    department_head = PublicCampusKeyOfficialSerializer(
        read_only=True,
    )

    class Meta:
        model = CampusUnit
        fields = [
            "uuid",
            "name",
            "slug",
            "short_description",
            "thumbnail",
            "display_order",
            "officials",
            "department_head",
        ]


class PublicCampusUnitRetrieveSerializer(serializers.ModelSerializer):
    officials = PublicCampusKeyOfficialSerializer(
        source="members", many=True, read_only=True
    )
    department_head = PublicCampusKeyOfficialSerializer(
        read_only=True,
    )

    class Meta:
        model = CampusUnit
        fields = [
            "uuid",
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
            "officials",
            "department_head",
        ]


class PublicResearchFacilityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchFacility
        fields = [
            "uuid",
            "name",
            "slug",
            "short_description",
            "thumbnail",
            "display_order",
        ]


class PublicResearchFacilityRetrieveSerializer(serializers.ModelSerializer):
    detailed_description = serializers.CharField(source="description", read_only=True)

    class Meta:
        model = ResearchFacility
        fields = [
            "uuid",
            "name",
            "slug",
            "short_description",
            "detailed_description",
            "objectives",
            "thumbnail",
            "display_order",
        ]


class PublicGlobalGallerySerializer(serializers.Serializer):
    uuid = serializers.CharField()
    image = serializers.CharField(allow_blank=True, allow_null=True)
    caption = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    source_type = serializers.CharField()
    source_identifier = serializers.CharField()
    source_name = serializers.CharField()
    source_context = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.DateTimeField()


class PublicGlobalEventSerializer(serializers.ModelSerializer):
    unions = PublicCampusUnionCompactSerializer(many=True, read_only=True)
    clubs = serializers.SerializerMethodField()
    departments = serializers.SerializerMethodField()

    class Meta:
        model = GlobalEvent
        fields = [
            "uuid",
            "title",
            "description",
            "event_type",
            "event_start_date",
            "event_end_date",
            "thumbnail",
            "registration_link",
            "location",
            "is_approved_by_department",
            "is_approved_by_campus",
            "unions",
            "clubs",
            "departments",
            "created_at",
        ]

    def _serialize_relationship(self, queryset):
        return [{"uuid": str(item.uuid), "name": item.name} for item in queryset.all()]

    def get_clubs(self, obj):
        return self._serialize_relationship(obj.clubs)

    def get_departments(self, obj):
        return self._serialize_relationship(obj.departments)
