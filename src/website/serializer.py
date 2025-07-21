# Rest Framework Import
from rest_framework import serializers
from typing import Any, List

# Project Imports
from src.website.models import CampusInfo, SocialMediaLink


class PublicSocialMediaLinkForCampusInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaLink
        fields = ["platform", "url"]


class PublicCampusInfoSerializer(serializers.ModelSerializer):
    social_links = serializers.SerializerMethodField()

    class Meta:
        model = CampusInfo
        fields = ["name", "phone_number", "email", "location", "social_links"]

    def get_social_links(self, obj) -> List[dict]:
        links = SocialMediaLink.objects.all()
        return PublicSocialMediaLinkForCampusInfoSerializer(links, many=True).data
