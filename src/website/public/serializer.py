from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

# Project Imports
from src.website.models import (
    CampusInfo,
    SocialMediaLink,
    CampusDownload,
    CampusEvent,
    CampusKeyOfficial,
    CampusEventGallery,
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
            "photo",
            "email",
            "phone_number",
        ]
