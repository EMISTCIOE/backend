from rest_framework import serializers

from src.base.serializers import AbstractInfoRetrieveSerializer
from src.department.messages import (
    ACADEMIC_PROGRAM_CREATED_SUCCESS,
    ACADEMIC_PROGRAM_UPDATED_SUCCESS,
    DEPARTMENT_CREATED_SUCCESS,
    DEPARTMENT_DOWNLOAD_CREATED_SUCCESS,
    DEPARTMENT_DOWNLOAD_UPDATED_SUCCESS,
    DEPARTMENT_EVENT_CREATED_SUCCESS,
    DEPARTMENT_EVENT_UPDATED_SUCCESS,
    DEPARTMENT_PLAN_CREATED_SUCCESS,
    DEPARTMENT_PLAN_UPDATED_SUCCESS,
    DEPARTMENT_UPDATED_SUCCESS,
    DESRIPTION_OR_FILE_REQUIRED,
    EVENT_DATE_ERROR,
    PROGRAM_DEPARTMENT_MISMATCH,
)
from src.department.validators import (
    validate_department_download_file,
    validate_photo_thumbnail,
)
from src.libs.get_context import get_user_by_context
from src.libs.mixins import FileHandlingMixin

from .models import (
    AcademicProgram,
    Department,
    DepartmentDownload,
    DepartmentEvent,
    DepartmentEventGallery,
    DepartmentPlanAndPolicy,
    DepartmentSocialMedia,
)

# Department Serializers
# ------------------------------------------------------------------------------------------------------


class DepartmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = [
            "id",
            "name",
            "short_name",
            "email",
            "phone_no",
            "is_active",
            "thumbnail",
        ]


class DepartmentSocialMediaForDepartmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentSocialMedia
        fields = ["id", "platform", "url", "is_active"]


class DepartmentRetrieveSerializer(AbstractInfoRetrieveSerializer):
    social_links = DepartmentSocialMediaForDepartmentListSerializer(many=True)

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = Department
        fields = [
            "id",
            "name",
            "short_name",
            "brief_description",
            "detailed_description",
            "email",
            "phone_no",
            "thumbnail",
            "social_links",
        ]

        fields += AbstractInfoRetrieveSerializer.Meta.fields


class DepartmentSocialMediaForDepartmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentSocialMedia
        fields = ["platform", "url"]


class DepartmentCreateSerializer(serializers.ModelSerializer):
    social_links = DepartmentSocialMediaForDepartmentCreateSerializer(
        many=True,
        required=False,
    )
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
        required=False,
    )
    is_active = serializers.BooleanField(required=False, default=True)

    class Meta:
        model = Department
        fields = [
            "name",
            "short_name",
            "brief_description",
            "detailed_description",
            "email",
            "phone_no",
            "thumbnail",
            "social_links",
            "is_active",
        ]

    def create(self, validated_data):
        social_links = validated_data.pop("social_links", [])
        current_user = get_user_by_context(self.context)

        validated_data["name"] = validated_data.pop("name").strip().title()
        validated_data["short_name"] = validated_data.pop("short_name", "").strip()
        validated_data["created_by"] = current_user
        validated_data["is_active"] = validated_data.pop("is_active", True)

        instance = Department.objects.create(**validated_data)

        for social_link in social_links:
            social_link["department"] = instance
            social_link["created_by"] = current_user
            DepartmentSocialMedia.objects.create(**social_link)

        return instance

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": DEPARTMENT_CREATED_SUCCESS}


class DepartmentSocialMediaForDepartmentPatchSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=DepartmentSocialMedia.objects.filter(is_archived=False),
        required=False,
    )

    class Meta:
        model = DepartmentSocialMedia
        fields = ["id", "platform", "url", "is_active"]


class DepartmentPatchSerializer(FileHandlingMixin, serializers.ModelSerializer):
    social_links = DepartmentSocialMediaForDepartmentPatchSerializer(
        many=True,
        required=False,
    )
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Department
        fields = [
            "name",
            "short_name",
            "brief_description",
            "detailed_description",
            "email",
            "phone_no",
            "thumbnail",
            "social_links",
            "is_active",
        ]

    def update(self, instance, validated_data):
        social_links = validated_data.pop("social_links", [])
        current_user = get_user_by_context(self.context)

        self.handle_file_update(instance, validated_data, "thumbnail")

        # Sanitize the fields
        short_name = validated_data.pop("short_name", None)
        name = validated_data.pop("name", None)

        if short_name is not None:
            validated_data["short_name"] = short_name.strip()
        if name is not None:
            validated_data["name"] = name.strip().title()

        for key, val in validated_data.items():
            setattr(instance, key, val)

        # Handle Social Media Links
        for social_link_data in social_links:
            if "id" in social_link_data:
                obj = social_link_data.pop("id")
                social_link_data["updated_by"] = current_user

                for key, val in social_link_data.items():
                    setattr(obj, key, val)
                obj.save()
            else:
                social_link_data["department"] = instance
                social_link_data["created_by"] = current_user
                DepartmentSocialMedia.objects.create(**social_link_data)

        instance.updated_by = current_user
        instance.save()

        return instance

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": DEPARTMENT_UPDATED_SUCCESS}


class DepartmentListForOtherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "short_name", "thumbnail"]


# Academic Program Serializers
# ------------------------------------------------------------------------------------------------------


class AcademicProgramListSerializer(serializers.ModelSerializer):
    department = DepartmentListForOtherSerializer()

    class Meta:
        model = AcademicProgram
        fields = [
            "id",
            "name",
            "short_name",
            "program_type",
            "description",
            "department",
            "thumbnail",
            "is_active",
        ]


class AcademicProgramRetrieveSerializer(AbstractInfoRetrieveSerializer):
    department = DepartmentListForOtherSerializer()

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = AcademicProgram
        fields = [
            "id",
            "name",
            "department",
            "short_name",
            "program_type",
            "description",
            "thumbnail",
        ]
        fields += AbstractInfoRetrieveSerializer.Meta.fields


class AcademicProgramCreateSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
    )
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
    )

    class Meta:
        model = AcademicProgram
        fields = [
            "name",
            "short_name",
            "description",
            "program_type",
            "department",
            "thumbnail",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter department queryset based on user role
        user = get_user_by_context(self.context)
        if user and hasattr(user, 'role') and user.role == 'DEPARTMENT-ADMIN':
            if hasattr(user, 'department_id') and user.department_id:
                self.fields['department'].queryset = Department.objects.filter(
                    id=user.department_id, is_active=True
                )
            else:
                self.fields['department'].queryset = Department.objects.none()

    def validate_department(self, value):
        """Custom validation for department field"""
        user = get_user_by_context(self.context)
        
        if user and hasattr(user, 'role') and user.role == 'DEPARTMENT-ADMIN':
            if not hasattr(user, 'department_id') or user.department_id != value.id:
                raise serializers.ValidationError(
                    "Department admins can only create programs for their own department."
                )
        
        return value

    def create(self, validated_data):
        current_user = get_user_by_context(self.context)

        # sanitize
        validated_data["name"] = validated_data["name"].strip().title()
        validated_data["short_name"] = validated_data["short_name"].strip()
        validated_data["created_by"] = current_user

        return AcademicProgram.objects.create(**validated_data)

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": ACADEMIC_PROGRAM_CREATED_SUCCESS}


class AcademicProgramPatchSerializer(FileHandlingMixin, serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
    )
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
        required=False,
    )

    class Meta:
        model = AcademicProgram
        fields = [
            "name",
            "short_name",
            "description",
            "program_type",
            "department",
            "thumbnail",
            "is_active",
        ]

    def update(self, instance, validated_data):
        current_user = get_user_by_context(self.context)

        self.handle_file_update(instance, validated_data, "thumbnail")

        # Sanitize the fields
        short_name = validated_data.pop("short_name", None)
        name = validated_data.pop("name", None)

        if short_name is not None:
            validated_data["short_name"] = short_name.strip()
        if name is not None:
            validated_data["name"] = name.strip().title()

        for key, val in validated_data.items():
            setattr(instance, key, val)

        instance.updated_by = current_user
        instance.save()

        return instance

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": ACADEMIC_PROGRAM_UPDATED_SUCCESS}


class AcademicProgramListForOtherSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicProgram
        fields = ["id", "name", "short_name", "thumbnail"]


# Department Downloads Serializers
# ------------------------------------------------------------------------------------------------------


class DepartmentDownloadListSerializer(serializers.ModelSerializer):
    department = DepartmentListForOtherSerializer()

    class Meta:
        model = DepartmentDownload
        fields = ["id", "title", "file", "department", "description", "is_active"]


class DepartmentDownloadRetrieveSerializer(AbstractInfoRetrieveSerializer):
    department = DepartmentListForOtherSerializer()

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = DepartmentDownload
        fields = ["id", "title", "file", "department", "description"]
        fields += AbstractInfoRetrieveSerializer.Meta.fields


class DepartmentDownloadCreateSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
    )
    file = serializers.FileField(validators=[validate_department_download_file])

    class Meta:
        model = DepartmentDownload
        fields = ["title", "file", "department", "description"]

    def create(self, validated_data):
        current_user = get_user_by_context(self.context)

        # Sanitize text fields
        validated_data["title"] = validated_data["title"].strip()
        validated_data["created_by"] = current_user

        return DepartmentDownload.objects.create(**validated_data)

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": DEPARTMENT_DOWNLOAD_CREATED_SUCCESS}


class DepartmentDownloadPatchSerializer(FileHandlingMixin, serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
    )
    file = serializers.FileField(
        validators=[validate_department_download_file],
        required=False,
    )

    class Meta:
        model = DepartmentDownload
        fields = ["title", "file", "description", "department", "is_active"]

    def update(self, instance, validated_data):
        current_user = get_user_by_context(self.context)

        self.handle_file_update(instance, validated_data, "file")

        # Sanitize fields only if present
        title = validated_data.pop("title", None)
        if title is not None:
            instance.title = title.strip()

        description = validated_data.pop("description", None)
        if description is not None:
            instance.description = description.strip()

        if "department" in validated_data:
            instance.department = validated_data["department"]

        if "is_active" in validated_data:
            instance.is_active = validated_data["is_active"]

        instance.updated_by = current_user
        instance.save()

        return instance

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": DEPARTMENT_DOWNLOAD_UPDATED_SUCCESS}


# Department Events Serializers
# ------------------------------------------------------------------------------------------------------


class DepartmentEventGalleryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentEventGallery
        fields = ["id", "image", "caption", "is_active"]


class DepartmentEventListSerializer(serializers.ModelSerializer):
    department = DepartmentListForOtherSerializer()

    class Meta:
        model = DepartmentEvent
        fields = [
            "id",
            "title",
            "event_type",
            "event_start_date",
            "event_end_date",
            "thumbnail",
            "department",
            "is_active",
            "is_approved_by_department",
            "is_approved_by_campus",
        ]


class DepartmentEventRetrieveSerializer(AbstractInfoRetrieveSerializer):
    department = DepartmentListForOtherSerializer()
    gallery = DepartmentEventGalleryListSerializer(many=True, read_only=True)

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = DepartmentEvent
        fields = [
            "id",
            "title",
            "description_short",
            "description_detailed",
            "event_type",
            "event_start_date",
            "event_end_date",
            "thumbnail",
            "registration_link",
            "location",
            "department",
            "is_approved_by_department",
            "is_approved_by_campus",
            "gallery",
        ]
        fields += AbstractInfoRetrieveSerializer.Meta.fields


class DepartmentEventGalleryCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(validators=[validate_photo_thumbnail])

    class Meta:
        model = DepartmentEventGallery
        fields = ["image", "caption"]


class DepartmentEventCreateSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
    )
    gallery = DepartmentEventGalleryCreateSerializer(many=True, required=False)
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
    )

    class Meta:
        model = DepartmentEvent
        fields = [
            "title",
            "description_short",
            "description_detailed",
            "event_type",
            "event_start_date",
            "event_end_date",
            "thumbnail",
            "registration_link",
            "location",
            "department",
            "gallery",
        ]

    def validate(self, attrs):
        start = attrs.get("event_start_date")
        end = attrs.get("event_end_date")
        if start and end and end < start:
            raise serializers.ValidationError({"event_end_date": EVENT_DATE_ERROR})
        return attrs

    def create(self, validated_data):
        gallery_data = validated_data.pop("gallery", [])
        current_user = get_user_by_context(self.context)

        validated_data["title"] = validated_data["title"].strip().title()
        validated_data["description_short"] = validated_data[
            "description_short"
        ].strip()
        validated_data["created_by"] = current_user

        event = DepartmentEvent.objects.create(**validated_data)

        for image_data in gallery_data:
            image_data["event"] = event
            image_data["created_by"] = current_user
            DepartmentEventGallery.objects.create(**image_data)

        return event

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": DEPARTMENT_EVENT_CREATED_SUCCESS}


class DepartmentEventGalleryPatchSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=DepartmentEventGallery.objects.filter(is_archived=False),
        required=False,
    )
    image = serializers.ImageField(validators=[validate_photo_thumbnail])

    class Meta:
        model = DepartmentEventGallery
        fields = ["id", "image", "caption", "is_active"]


class DepartmentEventPatchSerializer(FileHandlingMixin, serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
    )
    gallery = DepartmentEventGalleryPatchSerializer(many=True, required=False)
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
        required=False,
    )

    class Meta:
        model = DepartmentEvent
        fields = [
            "title",
            "description_short",
            "description_detailed",
            "event_type",
            "event_start_date",
            "event_end_date",
            "thumbnail",
            "department",
            "gallery",
            "is_active",
        ]

    def validate(self, attrs):
        start = attrs.get("event_start_date")
        end = attrs.get("event_end_date")
        if start and end and end < start:
            raise serializers.ValidationError({"event_end_date": EVENT_DATE_ERROR})
        return attrs

    def update(self, instance, validated_data):
        gallery_data = validated_data.pop("gallery", [])
        current_user = get_user_by_context(self.context)

        self.handle_file_update(instance, validated_data, "thumbnail")

        # Update fields only if present
        if "title" in validated_data:
            validated_data["title"] = validated_data.pop("title").strip().title()

        for key, val in validated_data.items():
            setattr(instance, key, val)

        # Handle Event Gallery
        for gallery in gallery_data:
            if "id" in gallery:
                obj = gallery.pop("id")
                gallery["updated_by"] = current_user

                for key, val in gallery.items():
                    setattr(obj, key, val)
                obj.save()
            else:
                gallery["event"] = instance
                gallery["created_by"] = current_user
                DepartmentEventGallery.objects.create(**gallery)

        instance.updated_by = current_user
        instance.save()

        return instance

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": DEPARTMENT_EVENT_UPDATED_SUCCESS}


# Department Plans and Policies Serializers
# ------------------------------------------------------------------------------------------------------


class DepartmentPlanAndPolicyListSerializer(serializers.ModelSerializer):
    department = DepartmentListForOtherSerializer()

    class Meta:
        model = DepartmentPlanAndPolicy
        fields = ["id", "title", "file", "department", "description", "is_active"]


class DepartmentPlanAndPolicyRetrieveSerializer(AbstractInfoRetrieveSerializer):
    department = DepartmentListForOtherSerializer()

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = DepartmentPlanAndPolicy
        fields = ["id", "title", "file", "department", "description"]
        fields += AbstractInfoRetrieveSerializer.Meta.fields


class DepartmentPlanAndPolicyCreateSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
    )
    file = serializers.FileField(validators=[validate_department_download_file])
    title = serializers.CharField(required=True)

    class Meta:
        model = DepartmentPlanAndPolicy
        fields = ["title", "file", "department", "description"]

    def validate(self, attrs):
        description = attrs.get("description", "").strip()
        file = attrs.get("file")

        if not description and not file:
            raise serializers.ValidationError(
                {"description": DESRIPTION_OR_FILE_REQUIRED},
            )

        return attrs

    def create(self, validated_data):
        current_user = get_user_by_context(self.context)

        # Sanitize text fields
        validated_data["title"] = validated_data["title"].strip()
        validated_data["created_by"] = current_user

        return DepartmentPlanAndPolicy.objects.create(**validated_data)

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": DEPARTMENT_PLAN_CREATED_SUCCESS}


class DepartmentPlanAndPolicyPatchSerializer(
    FileHandlingMixin,
    serializers.ModelSerializer,
):
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
    )
    file = serializers.FileField(
        validators=[validate_department_download_file],
        required=False,
    )

    class Meta:
        model = DepartmentPlanAndPolicy
        fields = ["title", "file", "description", "department", "is_active"]

    def validate(self, attrs):
        description = attrs.get("description", "").strip()
        file = attrs.get("file")

        # Use incoming data or fallback to existing instance
        has_description = description is not None and bool(description)
        has_file = file is not None or (self.instance and self.instance.file)

        if not has_description and not has_file:
            raise serializers.ValidationError(
                {"description": DESRIPTION_OR_FILE_REQUIRED},
            )

        return attrs

    def update(self, instance, validated_data):
        current_user = get_user_by_context(self.context)

        self.handle_file_update(instance, validated_data, "file")

        # Sanitize fields only if present
        title = validated_data.pop("title", None)
        if title is not None:
            instance.title = title.strip()

        description = validated_data.pop("description", None)
        if description is not None:
            instance.description = description.strip()

        if "department" in validated_data:
            instance.department = validated_data["department"]

        if "is_active" in validated_data:
            instance.is_active = validated_data["is_active"]

        instance.updated_by = current_user
        instance.save()

        return instance

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": DEPARTMENT_PLAN_UPDATED_SUCCESS}
