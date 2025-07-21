from rest_framework import serializers

# Project Imports
from src.base.serializers import AbstractInfoRetrieveSerializer
from src.department.models import Department
from src.libs.get_context import get_user_by_context
from src.notice.constants import NoticeStatus
from src.notice.listing_apis.serializers import (
    CategoryForNoticeListSerializer,
    DepartmentForNoticeListSerializer,
    UserForNoticeListSerializer,
)
from src.notice.messages import (
    NOTICE_CREATE_SUCCESS,
    NOTICE_UPDATE_SUCCESS,
    TITLE_OR_MEDIA_REQUIRED,
)
from src.notice.validators import validate_notice_media_file

from .models import Notice, NoticeCategory, NoticeMedia


class NoticeMediaSerializerForNoticeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoticeMedia
        fields = ["id", "file", "caption", "media_type"]


class NoticeListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name")
    department_name = serializers.CharField(source="department.name")
    author_name = serializers.CharField(source="created_by.get_full_name")

    class Meta:
        model = Notice
        fields = [
            "id",
            "title",
            "slug",
            "thumbnail",
            "is_featured",
            "department",
            "status",
            "category",
            "department_name",
            "category_name",
            "published_at",
            "author_name",
        ]


class NoticeRetrieveSerializer(AbstractInfoRetrieveSerializer):
    department = DepartmentForNoticeListSerializer()
    category = CategoryForNoticeListSerializer()
    medias = NoticeMediaSerializerForNoticeListSerializer(many=True)
    author = UserForNoticeListSerializer(source="created_by")

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = Notice
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "thumbnail",
            "status",
            "is_featured",
            "department",
            "category",
            "published_at",
            "medias",
            "author",
        ]
        fields += AbstractInfoRetrieveSerializer.Meta.fields


class NoticeMediaSerializerForNoticeCreateSerializer(serializers.ModelSerializer):
    """Serializer for NoticeMedia model."""

    class Meta:
        model = NoticeMedia
        fields = ["file", "caption", "media_type"]

    def validate(self, data):
        """Validate media file type."""
        file = data.get("file")
        media_type = data.get("media_type")

        if file and media_type:
            validate_notice_media_file(file, media_type)

        return data


class NoticeCreateSerializer(serializers.ModelSerializer):
    """Serializer for Notice model, supporting media uploads."""

    medias = NoticeMediaSerializerForNoticeCreateSerializer(many=True, required=False)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
        allow_null=True,
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=NoticeCategory.objects.filter(is_active=True),
    )
    is_draft = serializers.BooleanField(default=False, write_only=True)

    class Meta:
        model = Notice
        fields = [
            "title",
            "department",
            "category",
            "thumbnail",
            "is_draft",
            "is_featured",
            "description",
            "medias",
        ]

    def validate(self, attrs):
        """Ensure notice has either a title or at least one media."""

        title = attrs.get("title", "").strip()
        medias = attrs.get("medias", [])

        if not title and not medias:
            raise serializers.ValidationError({"title": TITLE_OR_MEDIA_REQUIRED})

        return attrs

    def create(self, validated_data):
        user = get_user_by_context(self.context)
        medias_data = validated_data.pop("medias", [])

        notice = Notice.objects.create(
            title=validated_data.get("title", "").strip(),
            description=validated_data.get("description", "").strip(),
            department=validated_data["department"],
            is_featured=validated_data["is_featured"],
            category=validated_data["category"],
            created_by=user,
        )

        if validated_data["is_draft"]:
            notice.status = NoticeStatus.DRAFT.value
        else:
            notice.status = NoticeStatus.PENDING.value
        notice.save()

        notice_medias = [
            NoticeMedia(notice=notice, created_by=user, **media_data)
            for media_data in medias_data
        ]
        NoticeMedia.objects.bulk_create(notice_medias)

        return notice

    def to_representation(self, instance) -> dict[str:str]:
        return {"message": NOTICE_CREATE_SUCCESS}


class NoticeMediaSerializerForNoticePatchSerializer(serializers.ModelSerializer):
    """Serializer for NoticeMedia model for patch."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=NoticeMedia.objects.filter(is_active=True),
    )

    class Meta:
        model = NoticeMedia
        fields = ["id", "file", "caption", "media_type"]

    def validate(self, data):
        """Validate media file type."""
        file = data.get("file")
        media_type = data.get("media_type")

        if file and media_type:
            validate_notice_media_file(file, media_type)

        return data


class NoticePatchSerializer(serializers.ModelSerializer):
    medias = NoticeMediaSerializerForNoticeCreateSerializer(many=True, required=False)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=NoticeCategory.objects.filter(is_active=True),
        required=False,
    )
    is_draft = serializers.BooleanField(default=False, write_only=True)

    class Meta:
        model = Notice
        fields = [
            "title",
            "department",
            "category",
            "thumbnail",
            "is_draft",
            "is_featured",
            "description",
            "medias",
        ]

    def validate(self, attrs):
        """Ensure notice has either a title or at least one media."""
        title = attrs.get("title", "").strip()
        medias = attrs.get("medias", [])

        if not title and not medias:
            raise serializers.ValidationError({"title": TITLE_OR_MEDIA_REQUIRED})

        return attrs

    def update(self, instance: Notice, validated_data):
        user = get_user_by_context(self.context)
        medias_data = validated_data.pop("medias", [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value.strip() if isinstance(value, str) else value)

        if validated_data.get("is_draft", False):
            instance.status = NoticeStatus.DRAFT.value
        else:
            instance.status = NoticeStatus.PENDING.value

        # Update audit info
        instance.updated_by = user
        instance.save()

        if medias_data is not None:
            existing_medias = instance.medias.filter(is_active=True)
            incoming_ids = []

            for media_data in medias_data:
                media_id = media_data.get("id")

                if media_id:
                    # Update existing media
                    media_instance = existing_medias.filter(id=media_id.id).first()
                    if media_instance:
                        incoming_ids.append(media_instance.id)
                        for key, value in media_data.items():
                            setattr(media_instance, key, value)
                        media_instance.updated_by = user
                        media_instance.save()
                else:
                    # Create new media
                    NoticeMedia.objects.create(
                        notice=instance,
                        created_by=user,
                        **media_data,
                    )

        return instance

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": NOTICE_UPDATE_SUCCESS}


class NoticeStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating notice status only."""
    
    status = serializers.ChoiceField(choices=NoticeStatus.choices())
    
    class Meta:
        model = Notice
        fields = ["status"]         
        read_only_fields = []      

    def update(self, instance, validated_data):
        instance.status = validated_data["status"]
        instance.updated_by = get_user_by_context(self.context) 
        instance.save(update_fields=["status", "updated_by"])
        return instance

    def to_representation(self, instance):
        return {"message": NOTICE_STATUS_UPDATE_SUCCESS}