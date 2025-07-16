from rest_framework import serializers

# Project Imports
from src.base.serializers import AbstractInfoRetrieveSerializer
from src.department.models import Department
from src.libs.get_context import get_user_by_context
from src.notice.listing_apis.serializers import (
    CategoryForNoticeListSerializer,
    DepartmentForNoticeListSerializer,
    UserForNoticeListSerializer,
)
from src.notice.validators import validate_notice_media_file
from src.notice.messages import (
    NOTICE_CREATE_SUCCESS,
    NOTICE_UPDATE_SUCCESS,
    TITLE_OR_MEDIA_REQUIRED,
)
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
        fields = ["id", "file", "caption", "media_type"]

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
        queryset=Department.objects.all(),  # FIXME Active only
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=NoticeCategory.objects.filter(is_active=True),
    )

    class Meta:
        model = Notice
        fields = [
            "title",
            "department",
            "category",
            "thumbnail",
            "status",
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
            status=validated_data["status"],
            created_by=user,
        )

        notice_medias = [
            NoticeMedia(notice=notice, created_by=user, **media_data)
            for media_data in medias_data
        ]
        NoticeMedia.objects.bulk_create(notice_medias)

        return notice

    def to_representation(self, instance) -> dict[str:str]:
        return {"message": NOTICE_CREATE_SUCCESS}


class NoticePatchSerializer(serializers.ModelSerializer):
    medias = NoticeMediaSerializerForNoticeCreateSerializer(many=True, required=False)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),  # FIXME Active only
        required=False,
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=NoticeCategory.objects.filter(is_active=True),
        required=False,
    )

    class Meta:
        model = Notice
        fields = [
            "title",
            "department",
            "category",
            "thumbnail",
            "status",
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

        # Update audit info
        instance.updated_by = user
        instance.save()

        if medias_data:
            NoticeMedia.objects.filter(notice=instance).delete()
            media_instances = [
                NoticeMedia(notice=instance, created_by=user, **media)
                for media in medias_data
            ]
            NoticeMedia.objects.bulk_create(media_instances)

        return instance

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": NOTICE_UPDATE_SUCCESS}
