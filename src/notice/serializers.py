from django.core.files.storage import default_storage
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
    NOTICE_STATUS_UPDATE_SUCCESS,
    NOTICE_UPDATE_SUCCESS,
    TITLE_OR_MEDIA_REQUIRED,
)
from src.notice.validators import validate_notice_media_file

from .models import Notice, NoticeCategory, NoticeMedia
from src.user.models import User


class NoticeMediaForNoticeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoticeMedia
        fields = ["id", "file", "caption", "media_type"]


class NoticeListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name")
    department_name = serializers.SerializerMethodField()
    campus_unit_name = serializers.SerializerMethodField()
    campus_section_name = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Notice
        fields = [
            "id",
            "title",
            "slug",
            "thumbnail",
            "is_featured",
            "is_approved_by_department",
            "is_approved_by_campus",
            "department",
            "campus_unit",
            "campus_section",
            "status",
            "category",
            "department_name",
            "campus_unit_name",
            "campus_section_name",
            "category_name",
            "published_at",
            "author_name",
        ]

    def get_department_name(self, obj) -> str:
        return obj.department.name if obj.department else ""

    def get_campus_unit_name(self, obj) -> str:
        return obj.campus_unit.name if obj.campus_unit else ""

    def get_campus_section_name(self, obj) -> str:
        return obj.campus_section.name if obj.campus_section else ""

    def get_author_name(self, obj) -> str:
        return obj.created_by.get_full_name() if obj.created_by else ""


class NoticeRetrieveSerializer(AbstractInfoRetrieveSerializer):
    department = DepartmentForNoticeListSerializer(allow_null=True)
    category = CategoryForNoticeListSerializer()
    medias = NoticeMediaForNoticeListSerializer(many=True)
    author = UserForNoticeListSerializer(source="created_by")
    campus_unit_name = serializers.SerializerMethodField()
    campus_section_name = serializers.SerializerMethodField()

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = Notice
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "thumbnail",
            "is_approved_by_department",
            "is_approved_by_campus",
            "status",
            "is_featured",
            "department",
            "campus_unit",
            "campus_section",
            "category",
            "campus_unit_name",
            "campus_section_name",
            "published_at",
            "medias",
            "author",
        ]
        fields += AbstractInfoRetrieveSerializer.Meta.fields

    def get_campus_unit_name(self, obj) -> str:
        return obj.campus_unit.name if obj.campus_unit else ""

    def get_campus_section_name(self, obj) -> str:
        return obj.campus_section.name if obj.campus_section else ""


class NoticeMediaForNoticeCreateSerializer(serializers.ModelSerializer):
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

    medias = NoticeMediaForNoticeCreateSerializer(many=True, required=False)
    thumbnail = serializers.ImageField(allow_null=True, required=False)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
        allow_null=True,
        required=False,
    )
    campus_unit = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.none(),  # replaced in __init__
        allow_null=True,
        required=False,
    )
    campus_section = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.none(),  # replaced in __init__
        allow_null=True,
        required=False,
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
            "campus_unit",
            "campus_section",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from src.website.models import CampusUnit, CampusSection

        self.fields["campus_unit"].queryset = CampusUnit.objects.filter(is_active=True)
        self.fields["campus_section"].queryset = CampusSection.objects.filter(is_active=True)

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
        campus_unit = validated_data.pop("campus_unit", None)
        campus_section = validated_data.pop("campus_section", None)

        # Enforce scope for campus unit/section roles
        if user.role == User.RoleType.CAMPUS_UNIT:
            if user.campus_unit is None:
                raise serializers.ValidationError({"campus_unit": "Your account is not linked to a campus unit."})
            if campus_unit and campus_unit != user.campus_unit:
                raise serializers.ValidationError({"campus_unit": "You can only post notices for your campus unit."})
            campus_unit = user.campus_unit

        if user.role == User.RoleType.CAMPUS_SECTION:
            if user.campus_section is None:
                raise serializers.ValidationError({"campus_section": "Your account is not linked to a campus section."})
            if campus_section and campus_section != user.campus_section:
                raise serializers.ValidationError({"campus_section": "You can only post notices for your campus section."})
            campus_section = user.campus_section

        notice = Notice.objects.create(
            title=(validated_data.get("title") or "").strip(),
            description=(validated_data.get("description") or "").strip(),
            department=validated_data.get("department"),
            campus_unit=campus_unit,
            campus_section=campus_section,
            thumbnail=validated_data.get("thumbnail", None),
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


class NoticeMediaForNoticePatchSerializer(serializers.ModelSerializer):
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
    medias = NoticeMediaForNoticePatchSerializer(many=True, required=False)
    thumbnail = serializers.ImageField(allow_null=True, required=False)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    campus_unit = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.none(),  # replaced in __init__
        required=False,
        allow_null=True,
    )
    campus_section = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.none(),  # replaced in __init__
        required=False,
        allow_null=True,
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=NoticeCategory.objects.filter(is_active=True),
        required=False,
    )
    is_draft = serializers.BooleanField(required=False)

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
            "campus_unit",
            "campus_section",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from src.website.models import CampusUnit, CampusSection

        self.fields["campus_unit"].queryset = CampusUnit.objects.filter(is_active=True)
        self.fields["campus_section"].queryset = CampusSection.objects.filter(is_active=True)

    def validate(self, attrs):
        """Ensure notice has either a title or at least one media."""
        title = attrs.get("title", self.instance.title).strip()
        medias = attrs.get("medias", self.instance.medias)

        if not title and not medias:
            raise serializers.ValidationError({"title": TITLE_OR_MEDIA_REQUIRED})

        return attrs

    def update(self, instance: Notice, validated_data):
        user = get_user_by_context(self.context)
        medias_data = validated_data.pop("medias", [])
        campus_unit = validated_data.pop("campus_unit", getattr(self.instance, "campus_unit", None))
        campus_section = validated_data.pop("campus_section", getattr(self.instance, "campus_section", None))

        # Handle the thumbnail
        if "thumbnail" in validated_data:
            if instance.thumbnail and default_storage.exists(instance.thumbnail.name):
                default_storage.delete(instance.thumbnail.name)

            instance.thumbnail = validated_data.pop("thumbnail", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value.strip() if isinstance(value, str) else value)

        # Enforce scoping for campus unit/section roles
        if user.role == User.RoleType.CAMPUS_UNIT:
            if user.campus_unit is None:
                raise serializers.ValidationError({"campus_unit": "Your account is not linked to a campus unit."})
            if campus_unit and campus_unit != user.campus_unit:
                raise serializers.ValidationError({"campus_unit": "You can only manage notices for your campus unit."})
            campus_unit = user.campus_unit

        if user.role == User.RoleType.CAMPUS_SECTION:
            if user.campus_section is None:
                raise serializers.ValidationError({"campus_section": "Your account is not linked to a campus section."})
            if campus_section and campus_section != user.campus_section:
                raise serializers.ValidationError({"campus_section": "You can only manage notices for your campus section."})
            campus_section = user.campus_section

        instance.campus_unit = campus_unit
        instance.campus_section = campus_section

        if "is_draft" in validated_data:
            if validated_data["is_draft"]:
                instance.status = NoticeStatus.DRAFT.value
            else:
                instance.status = NoticeStatus.PENDING.value

        # Update audit info
        instance.updated_by = user
        instance.save()

        # Update notice medias
        if medias_data is not None:
            for media_data in medias_data:
                media_instance = media_data.pop("id", None)
                if media_instance:
                    # Remove the old file from disk
                    if media_instance.file and default_storage.exists(
                        media_instance.file.name,
                    ):
                        default_storage.delete(media_instance.file.name)

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

    def update(self, instance, validated_data):
        instance.status = validated_data["status"]
        instance.updated_by = get_user_by_context(self.context)
        instance.save(update_fields=["status", "updated_by"])
        return instance

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": NOTICE_STATUS_UPDATE_SUCCESS}
