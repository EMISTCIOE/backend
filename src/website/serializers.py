from rest_framework import serializers
from .models import CampusInfo, SocialMediaLink
from src.libs.get_context import get_user_by_context

class SocialMediaLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaLink
        fields = [
            "id", "platform", "url", "is_active", "is_archived"
        ]

class CampusInfoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusInfo
        fields = [
            "id", "name", "phone_number", "email", "location",
            "organization_chart", "is_active", "is_archived"
        ]

class CampusInfoRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusInfo
        fields = [
            "id", "name", "phone_number", "email", "location", "organization_chart",
            "is_active", "is_archived"
        ]

class CampusInfoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusInfo
        fields = [
            "name", "phone_number", "email", "location",
            "organization_chart", "is_active", "is_archived"
        ]

    def create(self, validated_data):
        created_by = get_user_by_context(self.context)
        validated_data['created_by'] = created_by
        campus = CampusInfo.objects.create(**validated_data)
        return campus

    def to_representation(self, instance):
        return {"message": "Campus Info created successfully", "id": instance.id}
