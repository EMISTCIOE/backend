from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

# Project Imports
from src.website.models import (
    CampusDownload,
    CampusEvent,
    CampusEventGallery,
    CampusFeedback,
    CampusInfo,
    CampusKeyOfficial,
    SocialMediaLink,
)
from src.website.public.messages import (
    FEEDBACK_FULL_NAME_REQUIRED,
    FEEDBACK_MESSAGE_TOO_SHORT,
)


class PublicEventGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusEventGallery
        fields = ["id", "image", "caption"]


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
        fields = ["id", "title", "description", "file", "created_at"]


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


class PublicCampusEventRetrieveSerializer(serializers.ModelSerializer):
    gallery = PublicEventGallerySerializer(many=True, read_only=True)

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
