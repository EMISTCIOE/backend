from rest_framework import serializers
from src.website.models import CampusInfo, SocialMediaLink


class SocialMediaLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaLink
        fields = ["platform", "url"]


class CampusInfoPublicSerializer(serializers.ModelSerializer):
    social_links = serializers.SerializerMethodField()

    class Meta:
        model = CampusInfo
        fields = ["name", "phone_number", "email", "location", "social_links"]

    def get_social_links(self, obj):
        links = SocialMediaLink.objects.all()
        return SocialMediaLinkSerializer(links, many=True).data
