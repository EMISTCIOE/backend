from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

# Project Imports
from src.website.models import CampusInfo, SocialMediaLink, CampusDownload, CampusEvent


class PublicSocialMediaLinkForCampusInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaLink
        fields = ["platform", "url"]


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
            SocialMediaLink.objects.filter(is_active=True), many=True
        ).data


class PublicCampusDownloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusDownload
        fields = ["id", "title", "description", "file", "created_at"]


class PublicCampusEventListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusEvent
        exclude = ["description_detailed"]


class PublicCampusEventRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusEvent
        fields = "__all__"
