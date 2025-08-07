from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

# Project Imports
from src.core.models import FiscalSessionBS
from src.website.models import (
    AcademicCalendar,
    CampusDownload,
    CampusEvent,
    CampusEventGallery,
    CampusFeedback,
    CampusInfo,
    CampusKeyOfficial,
    CampusReport,
    CampusUnion,
    CampusUnionMember,
    SocialMediaLink,
    StudentClub,
    StudentClubEvent,
    StudentClubEventGallery,
    StudentClubMember,
)
from src.website.public.messages import (
    FEEDBACK_FULL_NAME_REQUIRED,
    FEEDBACK_MESSAGE_TOO_SHORT,
)


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


class PublicCampusEventListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusEvent
        fields = [
            "uuid",
            "title",
            "description_short",
            "event_type",
            "event_start_date",
            "event_end_date",
            "thumbnail",
        ]


class PublicEventGalleryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusEventGallery
        fields = ["uuid", "image", "caption"]


class PublicCampusEventRetrieveSerializer(serializers.ModelSerializer):
    gallery = PublicEventGalleryListSerializer(many=True)

    class Meta:
        model = CampusEvent
        fields = [
            "uuid",
            "title",
            "description_short",
            "description_detailed",
            "event_type",
            "event_start_date",
            "event_end_date",
            "thumbnail",
            "gallery",
        ]


class PublicCampusKeyOfficialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusKeyOfficial
        fields = [
            "uuid",
            "title_prefix",
            "full_name",
            "designation",
            "message",
            "photo",
            "email",
            "phone_number",
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
    class Meta:
        model = CampusUnion
        fields = ["uuid", "name", "thumbnail", "short_description"]


class PublicCampusUnionRetrieveSerializer(serializers.ModelSerializer):
    members = PublicCampusUnionMemberSerializer(many=True, read_only=True)

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
        ]


class PublicStudentClubMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClubMember
        fields = ["uuid", "full_name", "designation", "photo"]


class PublicStudentClubListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClub
        fields = ["uuid", "name", "short_description", "thumbnail"]


class PublicStudentClubRetrieveSerializer(serializers.ModelSerializer):
    members = PublicStudentClubMemberSerializer(many=True, read_only=True)

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
        ]


class PublicStudentClubEventGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClubEventGallery
        fields = ["uuid", "image", "caption", "created_at"]


class PublicStudentClubEventListSerializer(serializers.ModelSerializer):
    club_name = serializers.CharField(source="club.name", read_only=True)

    class Meta:
        model = StudentClubEvent
        fields = ["uuid", "title", "club_name", "date", "thumbnail"]


class PublicStudentClubEventRetrieveSerializer(serializers.ModelSerializer):
    club_name = serializers.CharField(source="club.name", read_only=True)
    gallery = PublicStudentClubEventGallerySerializer(many=True, read_only=True)

    class Meta:
        model = StudentClubEvent
        fields = [
            "uuid",
            "title",
            "description",
            "date",
            "thumbnail",
            "club_name",
            "gallery",
        ]
