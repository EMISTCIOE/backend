from rest_framework import serializers

from src.libs.get_context import get_user_by_context

from ..base.serializers import AbstractInfoRetrieveSerializer
from ..user.validators import validate_user_image
from .constants import CAMPUS_KEY_OFFICIAL_FILE_PATH
from .models import CampusInfo, CampusKeyOfficial, SocialMediaLink


class SocialMediaLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaLink
        fields = ["id", "platform", "url", "is_active"]


class CampusInfoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusInfo
        fields = [
            "id",
            "name",
            "phone_number",
            "email",
            "location",
            "organization_chart",
            "is_active",
        ]


class CampusInfoRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusInfo
        fields = [
            "id",
            "name",
            "phone_number",
            "email",
            "location",
            "organization_chart",
            "is_active",
        ]


class CampusInfoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusInfo
        fields = [
            "name",
            "phone_number",
            "email",
            "location",
            "organization_chart",
            "is_active",
            "is_archived",
        ]

    def create(self, validated_data):
        created_by = get_user_by_context(self.context)
        validated_data["created_by"] = created_by
        campus = CampusInfo.objects.create(**validated_data)
        return campus

    def to_representation(self, instance):
        return {"message": "Campus Info created successfully", "id": instance.id}


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
            "photo",
            "email",
            "phone_number",
            "is_active",
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
            "phone_number",
            "is_active",
        ]

    def create(self, validated_data):
        created_by = get_user_by_context(self.context)
        validated_data["created_by"] = created_by
        validated_data["full_name"] = validated_data.pop("full_name").title()

        return CampusKeyOfficial.objects.create(**validated_data)


class CampusKeyOfficialPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusKeyOfficial
        fields = [
            "title_prefix",
            "full_name",
            "designation",
            "photo",
            "email",
            "phone_number",
            "is_active",
        ]

    def update(self, instance, validated_data):
        updated_by = get_user_by_context(self.context)
        validated_data["full_name"] = validated_data.pop("full_name").title()
        photo = validated_data.pop("photo", None)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        if photo:
            if photo is not None:
                upload_path = instance.get_upload_path(
                    upload_path=CAMPUS_KEY_OFFICIAL_FILE_PATH,
                    filename=photo.name,
                )
                instance.photo.delete(save=False)  # Remove the old file
                instance.photo.save(upload_path, photo)
            else:
                instance.photo.delete(
                    save=True,
                )  # Delete the existing photo if photo is None

        instance.updated_by = updated_by
        instance.save()
        return instance
