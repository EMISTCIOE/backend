from django.core.files.storage import default_storage
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from src.base.serializers import AbstractInfoRetrieveSerializer

# Project Imports
from src.core.models import FiscalSessionBS
from src.libs.get_context import get_user_by_context
from src.libs.mixins import FileHandlingMixin
from src.libs.validators import validate_unique_fields
from src.website.validators import (
    validate_campus_download_file,
    validate_photo_thumbnail,
)

from .messages import (
    ACADEMIC_CALENDER_CREATED_SUCCESS,
    ACADEMIC_CALENDER_UPDATED_SUCCESS,
    CAMPUS_CLUB_CREATED_SUCCESS,
    CAMPUS_CLUB_UPDATED_SUCCESS,
    CAMPUS_DOWNLOAD_CREATED_SUCCESS,
    CAMPUS_DOWNLOAD_UPDATED_SUCCESS,
    CAMPUS_EVENT_CREATED_SUCCESS,
    CAMPUS_EVENT_UPDATED_SUCCESS,
    CAMPUS_INFO_UPDATED_SUCCESS,
    CAMPUS_KEY_OFFICIAL_CREATE_SUCCESS,
    CAMPUS_KEY_OFFICIAL_UPDATE_SUCCESS,
    CAMPUS_REPORT_CREATED_SUCCESS,
    CAMPUS_REPORT_UPDATED_SUCCESS,
    CAMPUS_UNION_CREATED_SUCCESS,
    CAMPUS_UNION_UPDATED_SUCCESS,
    EVENT_DATE_ERROR,
    SOCIAL_MEDIA_ALREADY_EXISTS,
    STUDENT_CLUB_EVENT_CREATED_SUCCESS,
    STUDENT_CLUB_EVENT_UPDATED_SUCCESS,
    YEAR_ORDER_ERROR,
)
from .models import (
    AcademicCalendar,
    CampusDownload,
    CampusEvent,
    CampusEventGallery,
    CampusFeedback,
    CampusInfo,
    CampusKeyOfficial,
    CampusReport,
    CampusUnion,
    CampusUnionMember,
    SocialMediaLink,
    StudentClub,
    StudentClubEvent,
    StudentClubEventGallery,
    StudentClubMember,
)

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

        if "name" in validated_data:
            validated_data["name"] = validated_data.pop("name").strip().title()

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
    photo = serializers.ImageField(
        allow_null=True, validators=[validate_photo_thumbnail]
    )

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
            if instance.photo and default_storage.exists(instance.photo.name):
                default_storage.delete(instance.photo.name)

            instance.photo = validated_data.pop("photo", None)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.updated_by = updated_by
        instance.save()
        return instance

    def to_representation(self, instance):
        return {"message": CAMPUS_KEY_OFFICIAL_UPDATE_SUCCESS}


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
        validators=[validate_campus_download_file],
        required=False,
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
        queryset=FiscalSessionBS.objects.filter(is_active=True),
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
        queryset=FiscalSessionBS.objects.filter(is_active=True),
        required=False,
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


# Campus Reports Serializers
# ------------------------------------------------------------------------------------------------------


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


# Campus Events Serializers
# ------------------------------------------------------------------------------------------------------


class CampusEventGalleryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusEventGallery
        fields = ["id", "image", "caption", "is_active"]


class CampusEventListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusEvent
        fields = [
            "id",
            "title",
            "event_type",
            "event_start_date",
            "event_end_date",
            "thumbnail",
            "is_active",
        ]


class CampusEventRetrieveSerializer(AbstractInfoRetrieveSerializer):
    gallery = CampusEventGalleryListSerializer(many=True, read_only=True)

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = CampusEvent
        fields = [
            "id",
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


class CampusEventGalleryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusEventGallery
        fields = ["image", "caption"]


class CampusEventCreateSerializer(serializers.ModelSerializer):
    gallery = CampusEventGalleryCreateSerializer(many=True, required=False)
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
    )

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

        event = CampusEvent.objects.create(**validated_data)

        for image_data in gallery_data:
            image_data["event"] = event
            image_data["created_by"] = current_user
            CampusEventGallery.objects.create(**image_data)

        return event

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": CAMPUS_EVENT_CREATED_SUCCESS}


class CampusEventGalleryPatchSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=CampusEventGallery.objects.filter(is_archived=False),
        required=False,
    )

    class Meta:
        model = CampusEventGallery
        fields = ["id", "image", "caption", "is_active"]


class CampusEventPatchSerializer(FileHandlingMixin, serializers.ModelSerializer):
    gallery = CampusEventGalleryPatchSerializer(many=True, required=False)
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
        required=False,
    )

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
                CampusEventGallery.objects.create(**gallery)

        instance.updated_by = current_user
        instance.save()

        return instance

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": CAMPUS_EVENT_UPDATED_SUCCESS}


# Campus Union Serializers
# ------------------------------------------------------------------------------------------------------


class CampusUnionMemberListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusUnionMember
        fields = ["id", "full_name", "designation", "photo", "is_active"]


class CampusUnionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusUnion
        fields = ["id", "name", "description", "is_active"]


class CampusUnionRetrieveSerializer(AbstractInfoRetrieveSerializer):
    members = CampusUnionMemberListSerializer(many=True)

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = CampusUnion
        fields = ["id", "name", "description", "members"]

        fields += AbstractInfoRetrieveSerializer.Meta.fields


class CampusUnionMemberCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusUnionMember
        fields = ["full_name", "designation", "photo"]


class CampusUnionCreateSerializer(serializers.ModelSerializer):
    members = CampusUnionMemberCreateSerializer(many=True, allow_null=True)

    class Meta:
        model = CampusUnion
        fields = ["name", "description", "members"]

    def create(self, validated_data):
        current_user = get_user_by_context(self.context)
        members_data = validated_data.pop("members", [])

        validated_data["name"] = validated_data["name"].strip()
        validated_data["created_by"] = current_user
        union = CampusUnion.objects.create(**validated_data)

        for member_data in members_data:
            CampusUnionMember.objects.create(
                union=union,
                **member_data,
                created_by=current_user,
            )

        return union

    def to_representation(self, instance):
        return {"message": CAMPUS_UNION_CREATED_SUCCESS}


class CampusUnionMemberPatchSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=CampusUnionMember.objects.filter(is_archived=False),
        required=False,
    )

    class Meta:
        model = CampusUnionMember
        fields = ["id", "full_name", "designation", "photo", "is_active"]


class CampusUnionPatchSerializer(serializers.ModelSerializer):
    members = CampusUnionMemberPatchSerializer(many=True, required=False)

    class Meta:
        model = CampusUnion
        fields = ["name", "description", "members", "is_active"]

    def update(self, instance, validated_data):
        current_user = get_user_by_context(self.context)
        union_members = validated_data.pop("members", [])

        name = validated_data.pop("name", None)
        if name is not None:
            instance.name = name.strip()

        for k, v in validated_data.items():
            setattr(instance, k, v)

        # Handle union members
        for union_member_data in union_members:
            if "id" in union_member_data:
                obj = union_member_data.pop("id")
                union_member_data["updated_by"] = current_user

                for key, val in union_member_data.items():
                    setattr(obj, key, val)
                obj.save()
            else:
                union_member_data["union"] = instance
                union_member_data["created_by"] = current_user
                CampusUnionMember.objects.create(**union_member_data)

        instance.updated_by = current_user
        instance.save()
        return instance

    def to_representation(self, instance):
        return {"message": CAMPUS_UNION_UPDATED_SUCCESS}


# Student Club Serializers
# ------------------------------------------------------------------------------------------------------


class StudentClubMemberListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClubMember
        fields = ["id", "full_name", "designation", "photo", "is_active"]


class StudentClubListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClub
        fields = ["id", "name", "short_description", "thumbnail", "is_active"]


class StudentClubRetrieveSerializer(AbstractInfoRetrieveSerializer):
    members = StudentClubMemberListSerializer(many=True)

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = StudentClub
        fields = [
            "id",
            "name",
            "short_description",
            "thumbnail",
            "detailed_description",
            "members",
        ]

        fields += AbstractInfoRetrieveSerializer.Meta.fields


class StudentClubMemberCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClubMember
        fields = ["full_name", "designation", "photo"]


class StudentClubCreateSerializer(serializers.ModelSerializer):
    members = StudentClubMemberCreateSerializer(many=True, allow_null=True)
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
        required=False,
    )

    class Meta:
        model = StudentClub
        fields = [
            "name",
            "short_description",
            "thumbnail",
            "detailed_description",
            "members",
        ]

    def create(self, validated_data):
        current_user = get_user_by_context(self.context)
        members_data = validated_data.pop("members", [])

        validated_data["name"] = validated_data["name"].strip()
        validated_data["created_by"] = current_user
        club = StudentClub.objects.create(**validated_data)

        for member_data in members_data:
            StudentClubMember.objects.create(
                club=club,
                **member_data,
                created_by=current_user,
            )

        return club

    def to_representation(self, instance):
        return {"message": CAMPUS_CLUB_CREATED_SUCCESS}


class StudentClubMemberPatchSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=StudentClubMember.objects.filter(is_archived=False),
        required=False,
    )

    class Meta:
        model = StudentClubMember
        fields = ["id", "full_name", "designation", "photo", "is_active"]


class StudentClubPatchSerializer(FileHandlingMixin, serializers.ModelSerializer):
    members = StudentClubMemberPatchSerializer(many=True, required=False)
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
        required=False,
    )

    class Meta:
        model = StudentClub
        fields = [
            "name",
            "short_description",
            "thumbnail",
            "detailed_description",
            "members",
            "is_active",
        ]

    def update(self, instance, validated_data):
        current_user = get_user_by_context(self.context)
        club_members = validated_data.pop("members", [])

        self.handle_file_update(instance, validated_data, "thumbnail")

        name = validated_data.pop("name", None)
        if name is not None:
            instance.name = name.strip()

        for k, v in validated_data.items():
            setattr(instance, k, v)

        # Handle club members
        for club_member_data in club_members:
            if "id" in club_member_data:
                obj = club_member_data.pop("id")
                club_member_data["updated_by"] = current_user

                for key, val in club_member_data.items():
                    setattr(obj, key, val)
                obj.save()
            else:
                club_member_data["club"] = instance
                club_member_data["created_by"] = current_user
                StudentClubMember.objects.create(**club_member_data)

        instance.updated_by = current_user
        instance.save()
        return instance

    def to_representation(self, instance):
        return {"message": CAMPUS_CLUB_UPDATED_SUCCESS}


class StudentClubListForOtherSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClub
        fields = ["id", "name"]


# Student Club Events Serializers
# ------------------------------------------------------------------------------------------------------


class StudentClubEventGalleryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentClubEventGallery
        fields = ["id", "image", "caption", "is_active"]


class StudentClubEventListSerializer(serializers.ModelSerializer):
    club = StudentClubListForOtherSerializer()

    class Meta:
        model = StudentClubEvent
        fields = [
            "id",
            "title",
            "date",
            "thumbnail",
            "club",
            "is_active",
        ]


class StudentClubEventRetrieveSerializer(AbstractInfoRetrieveSerializer):
    club = StudentClubListForOtherSerializer()
    gallery = StudentClubEventGalleryListSerializer(many=True, read_only=True)

    class Meta(AbstractInfoRetrieveSerializer.Meta):
        model = StudentClubEvent
        fields = [
            "id",
            "title",
            "description",
            "date",
            "thumbnail",
            "club",
            "gallery",
        ]
        fields += AbstractInfoRetrieveSerializer.Meta.fields


class StudentClubEventGalleryCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(validators=[validate_photo_thumbnail])

    class Meta:
        model = StudentClubEventGallery
        fields = ["image", "caption"]


class StudentClubEventCreateSerializer(serializers.ModelSerializer):
    club = serializers.PrimaryKeyRelatedField(
        queryset=StudentClub.objects.filter(is_active=True),
    )
    gallery = StudentClubEventGalleryCreateSerializer(many=True, required=False)
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
    )

    class Meta:
        model = StudentClubEvent
        fields = [
            "title",
            "description",
            "date",
            "thumbnail",
            "club",
            "gallery",
        ]

    def create(self, validated_data):
        gallery_data = validated_data.pop("gallery", [])
        current_user = get_user_by_context(self.context)

        validated_data["title"] = validated_data["title"].strip().title()
        validated_data["description"] = validated_data.get("description", "").strip()
        validated_data["created_by"] = current_user

        event = StudentClubEvent.objects.create(**validated_data)

        for image_data in gallery_data:
            image_data["event"] = event
            image_data["created_by"] = current_user
            StudentClubEventGallery.objects.create(**image_data)

        return event

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": STUDENT_CLUB_EVENT_CREATED_SUCCESS}


class StudentClubEventGalleryPatchSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=StudentClubEventGallery.objects.filter(is_archived=False),
        required=False,
    )
    image = serializers.ImageField(validators=[validate_photo_thumbnail])

    class Meta:
        model = StudentClubEventGallery
        fields = ["id", "image", "caption", "is_active"]


class StudentClubEventPatchSerializer(FileHandlingMixin, serializers.ModelSerializer):
    club = serializers.PrimaryKeyRelatedField(
        queryset=StudentClub.objects.filter(is_active=True),
        required=False,
    )
    gallery = StudentClubEventGalleryPatchSerializer(many=True, required=False)
    thumbnail = serializers.ImageField(
        validators=[validate_photo_thumbnail],
        allow_null=True,
        required=False,
    )

    class Meta:
        model = StudentClubEvent
        fields = [
            "title",
            "description",
            "date",
            "thumbnail",
            "club",
            "gallery",
            "is_active",
        ]

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
                StudentClubEventGallery.objects.create(**gallery)

        instance.updated_by = current_user
        instance.save()

        return instance

    def to_representation(self, instance) -> dict[str, str]:
        return {"message": STUDENT_CLUB_EVENT_UPDATED_SUCCESS}
