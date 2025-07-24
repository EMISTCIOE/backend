from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from django.core.files.storage import default_storage

# Project Imports
from src.libs.get_context import get_user_by_context
from src.libs.validators import validate_unique_fields
from src.user.validators import validate_user_image
from src.base.serializers import AbstractInfoRetrieveSerializer

from .constants import CAMPUS_KEY_OFFICIAL_FILE_PATH
from .messages import (
    CAMPUS_INFO_UPDATED_SUCCESS,
    CAMPUS_KEY_OFFICIAL_CREATE_SUCCESS,
    CAMPUS_KEY_OFFICIAL_UPDATE_SUCCESS,
    SOCIAL_MEDIA_ALREADY_EXISTS,
)
from .models import CampusInfo, CampusKeyOfficial, SocialMediaLink


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

    def validate(self, attrs):
        return validate_unique_fields(
            model=SocialMediaLink,
            attrs=attrs,
            fields=["platform"],
            instance=self.instance or attrs.get("id"),
            error_messages={"platform": SOCIAL_MEDIA_ALREADY_EXISTS},
        )


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

    def update(self, instance, validated_data):
        user = get_user_by_context(self.context)
        social_links = validated_data.pop("social_links", [])
        validated_data["name"] = validated_data.pop("name").title()

        for key, val in validated_data.items():
            setattr(instance, key, val)

        for social_link in social_links:
            if "id" in social_link:
                sl = social_link.pop("id")
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
        return {"message": CAMPUS_INFO_UPDATED_SUCCESS, "id": instance.id}


# Campus Key Official Serializers
# ---------------------------------------------------------------------------------------------------


class CampusKeyOfficialListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusKeyOfficial
        fields = [
            "id",
            "title_prefix",
            "full_name",
            "designation",
            "photo",
            "email",
            "phone_number",
            "is_active",
        ]


class CampusKeyOfficialRetrieveSerializer(AbstractInfoRetrieveSerializer):
    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = CampusKeyOfficial
        fields = [
            "id",
            "title_prefix",
            "full_name",
            "designation",
            "message",
            "photo",
            "email",
            "phone_number",
        ]

        fields += AbstractInfoRetrieveSerializer.Meta.fields


class CampusKeyOfficialCreateSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(allow_null=True, validators=[validate_user_image])

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
            "is_active",
        ]

    def update(self, instance: CampusKeyOfficial, validated_data):
        updated_by = get_user_by_context(self.context)
        validated_data["full_name"] = validated_data.pop("full_name").title()

        # Handle the photo
        if "photo" in validated_data:
            if validated_data["photo"] is None:
                # Remove the old file from disk
                if instance.photo and default_storage.exists(instance.photo.name):
                    default_storage.delete(instance.photo.name)
            else:
                instance.photo = validated_data.pop("photo", None)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.updated_by = updated_by
        instance.save()
        return instance

    def to_representation(self, instance):
        return {"message": CAMPUS_KEY_OFFICIAL_UPDATE_SUCCESS}

class CampusDownloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusDownload
        fields = "__all__"

    def create(self, validated_data):
        validated_data['created_by'] = get_user_by_context(self.context)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_by'] = get_user_by_context(self.context)
        return super().update(instance, validated_data)