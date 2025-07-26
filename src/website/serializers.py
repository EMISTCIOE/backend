from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

# Project Imports
from src.libs.get_context import get_user_by_context
from src.base.serializers import AbstractInfoRetrieveSerializer
from src.user.validators import validate_user_image
from src.website.validators import validate_campus_download_file
from src.libs.mixins import FileHandlingMixin
from .constants import CAMPUS_KEY_OFFICIAL_FILE_PATH
from .messages import (
    ACADEMIC_CALENDER_CREATED_SUCCESS,
    ACADEMIC_CALENDER_UPDATED_SUCCESS,
    CAMPUS_DOWNLOAD_CREATED_SUCCESS,
    CAMPUS_DOWNLOAD_UPDATED_SUCCESS,
    CAMPUS_INFO_UPDATED_SUCCESS,
    CAMPUS_KEY_OFFICIAL_CREATE_SUCCESS,
    CAMPUS_KEY_OFFICIAL_UPDATE_SUCCESS,
    CAMPUS_REPORT_CREATED_SUCCESS,
    CAMPUS_REPORT_UPDATED_SUCCESS,
    SOCIAL_MEDIA_ALREADY_EXISTS,
    YEAR_ORDER_ERROR,
)
from .models import (
    AcademicCalendar,
    CampusDownload,
    CampusFeedback,
    CampusInfo,
    CampusKeyOfficial,
    CampusReport,
    SocialMediaLink,
    CampusEventGallery,
    FiscalSessionBS,
    CampusEvent,
)


# Campus Feedback Serializers
# ------------------------------------------------------------------------------------------------


class CampusFeedbackListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusFeedback
        fields = [
            "id",
            "full_name",
            "roll_number",
            "email",
            "message",
            "is_resolved",
            "created_at",
        ]


class CampusFeedbackResolveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusFeedback
        fields = ["is_resolved"]


# Campus Downloads Serializers
# ------------------------------------------------------------------------------------------------------


class CampusDownloadListSerializer(serializers.ModelSerializer):

    class Meta:
        model = CampusDownload
        fields = ["id", "title", "file", "description", "is_active"]


class CampusDownloadRetrieveSerializer(AbstractInfoRetrieveSerializer):

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = CampusDownload
        fields = ["id", "title", "file", "description"]
        fields += AbstractInfoRetrieveSerializer.Meta.fields


class CampusDownloadCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(validators=[validate_campus_download_file])

    class Meta:
        model = CampusDownload
        fields = ["title", "file", "description"]

    def create(self, validated_data):
        current_user = get_user_by_context(self.context)

        # Sanitize text fields
        validated_data["title"] = validated_data["title"].strip()
        validated_data["created_by"] = current_user

        return CampusDownload.objects.create(**validated_data)

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": CAMPUS_DOWNLOAD_CREATED_SUCCESS}


class CampusDownloadPatchSerializer(FileHandlingMixin, serializers.ModelSerializer):
    file = serializers.FileField(
        validators=[validate_campus_download_file], required=False
    )

    class Meta:
        model = CampusDownload
        fields = ["title", "file", "description", "is_active"]

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

        if "is_active" in validated_data:
            instance.is_active = validated_data["is_active"]

        instance.updated_by = current_user
        instance.save()

        return instance

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": CAMPUS_DOWNLOAD_UPDATED_SUCCESS}


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
        queryset=SocialMediaLink.objects.filter(is_archived=False), required=False
    )

    class Meta:
        model = SocialMediaLink
        fields = ["id", "platform", "url", "is_active"]

        extra_kwargs = {"platform": {"validators": []}}

    def validate(self, attrs):
        """Custom validation jasle uniqueness manyally handle garcha"""
        platform = attrs.get("platform")
        link_id = attrs.get("id", None)
        campus_info = self.context.get("campus_info")

        if platform and campus_info:
            social_media_query_set = SocialMediaLink.objects.filter(
                platform=platform,
                campus_info=campus_info,
                is_archived=False,
            )
            if link_id:
                social_media_query_set = social_media_query_set.exclude(pk=link_id)
            if social_media_query_set.exists():
                raise serializers.ValidationError(
                    {"platform": "Social Media Link with this Platform already exists."}
                )

        return attrs


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


# Campus Event Serializers
# ---------------------------------------------------------------------------------------------------


class CampusEventGalleryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusEventGallery
        fields = ["id", "image", "caption"]


class CampusEventGalleryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusEventGallery
        fields = ["image", "caption"]


class CampusEventListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusEvent
        fields = [
            "uuid",
            "title",
            "description_short",
            "event_type",
            "event_start_date",
            "event_end_date",
            "thumbnail",
        ]


class CampusEventRetrieveSerializer(AbstractInfoRetrieveSerializer):
    gallery = CampusEventGalleryListSerializer(many=True)

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = CampusEvent
        fields = [
            "uuid",
            "title",
            "description_short",
            "description_detailed",
            "event_type",
            "event_start_date",
            "event_end_date",
            "thumbnail",
            "gallery",
        ]
        fields += AbstractInfoRetrieveSerializer.Meta.fields


class CampusEventCreateSerializer(serializers.ModelSerializer):
    gallery = CampusEventGalleryCreateSerializer(many=True, required=False)

    class Meta:
        model = CampusEvent
        fields = [
            "title",
            "description_short",
            "description_detailed",
            "event_type",
            "event_start_date",
            "event_end_date",
            "thumbnail",
            "gallery",
            "is_active",
        ]

    def create(self, validated_data):
        gallery_data = validated_data.pop("gallery", [])
        user = get_user_by_context(self.context)
        event = CampusEvent.objects.create(**validated_data, created_by=user)

        for gallery_item in gallery_data:
            CampusEventGallery.objects.create(event=event, **gallery_item)

        return event


class CampusEventPatchSerializer(serializers.ModelSerializer):
    gallery = CampusEventGalleryCreateSerializer(many=True, required=False)

    class Meta:
        model = CampusEvent
        fields = [
            "title",
            "description_short",
            "description_detailed",
            "event_type",
            "event_start_date",
            "event_end_date",
            "thumbnail",
            "gallery",
            "is_active",
        ]

    def update(self, instance, validated_data):
        gallery_data = validated_data.pop("gallery", None)
        user = get_user_by_context(self.context)

        # Update simple fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.updated_by = user
        instance.save()

        # Update gallery if provided
        if gallery_data is not None:
            # Delete old gallery and add new
            instance.gallery.all().delete()
            for gallery_item in gallery_data:
                CampusEventGallery.objects.create(event=instance, **gallery_item)

        return instance


# Campus Reports Serializers
# ------------------------------------------------------------------------------------------------------


class FiscalSessionForCampusReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiscalSessionBS
        fields = ["id", "session_full", "session_short"]


class CampusReportListSerializer(serializers.ModelSerializer):
    fiscal_session = FiscalSessionForCampusReportSerializer()

    class Meta:
        model = CampusReport
        fields = [
            "id",
            "report_type",
            "fiscal_session",
            "published_date",
            "file",
            "is_active",
        ]


class CampusReportRetrieveSerializer(AbstractInfoRetrieveSerializer):
    fiscal_session = FiscalSessionForCampusReportSerializer()

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = CampusReport
        fields = [
            "id",
            "report_type",
            "fiscal_session",
            "published_date",
            "file",
        ]
        fields += AbstractInfoRetrieveSerializer.Meta.fields


class CampusReportCreateSerializer(serializers.ModelSerializer):
    fiscal_session = serializers.PrimaryKeyRelatedField(
        queryset=FiscalSessionBS.objects.filter(is_active=True)
    )

    class Meta:
        model = CampusReport
        fields = ["report_type", "fiscal_session", "published_date", "file"]

    def create(self, validated_data):
        current_user = get_user_by_context(self.context)
        validated_data["created_by"] = current_user
        return CampusReport.objects.create(**validated_data)

    def to_representation(self, instance):
        return {"message": CAMPUS_REPORT_CREATED_SUCCESS}


class CampusReportPatchSerializer(FileHandlingMixin, serializers.ModelSerializer):
    fiscal_session = serializers.PrimaryKeyRelatedField(
        queryset=FiscalSessionBS.objects.filter(is_active=True), required=False
    )

    class Meta:
        model = CampusReport
        fields = [
            "report_type",
            "fiscal_session",
            "published_date",
            "file",
            "is_active",
        ]

    def update(self, instance, validated_data):
        current_user = get_user_by_context(self.context)

        self.handle_file_update(instance, validated_data, "file")

        for key, val in validated_data.items():
            setattr(instance, key, val)

        instance.updated_by = current_user
        instance.save()
        return instance

    def to_representation(self, instance):
        return {"message": CAMPUS_REPORT_UPDATED_SUCCESS}


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
            "email",
            "phone_number",
            "is_active",
        ]

    def update(self, instance: CampusKeyOfficial, validated_data):
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

    def to_representation(self, instance):
        return {"message": CAMPUS_KEY_OFFICIAL_UPDATE_SUCCESS}


class AcademicCalendarListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicCalendar
        fields = ["id", "program_type", "start_year", "end_year", "file", "is_active"]


class AcademicCalendarRetrieveSerializer(AbstractInfoRetrieveSerializer):
    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = AcademicCalendar
        fields = [
            "id",
            "program_type",
            "start_year",
            "end_year",
            "file",
        ]

        fields += AbstractInfoRetrieveSerializer.Meta.fields


class AcademicCalendarCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicCalendar
        fields = ["program_type", "start_year", "end_year", "file"]

    def validate(self, attrs):
        start = attrs.get("start_year")
        end = attrs.get("end_year")

        if start is None or end is None:
            return attrs

        if start >= end:
            raise serializers.ValidationError({"end_year": YEAR_ORDER_ERROR})

        return attrs

    def create(self, validated_data):
        current_user = get_user_by_context(self.context)
        validated_data["created_by"] = current_user
        return AcademicCalendar.objects.create(**validated_data)

    def to_representation(self, instance):
        return {"message": ACADEMIC_CALENDER_CREATED_SUCCESS}


class AcademicCalendarPatchSerializer(FileHandlingMixin, serializers.ModelSerializer):
    class Meta:
        model = AcademicCalendar
        fields = ["program_type", "start_year", "end_year", "file", "is_active"]

    def validate(self, attrs):
        start = attrs.get("start_year", getattr(self.instance, "start_year", None))
        end = attrs.get("end_year", getattr(self.instance, "end_year", None))

        if start is not None and end is not None and start >= end:
            raise serializers.ValidationError({"end_year": YEAR_ORDER_ERROR})

        return attrs

    def update(self, instance, validated_data):
        current_user = get_user_by_context(self.context)

        self.handle_file_update(instance, validated_data, "file")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.updated_by = current_user
        instance.save()
        return instance

    def to_representation(self, instance):
        return {"message": ACADEMIC_CALENDER_UPDATED_SUCCESS}
