# Rest Framework Imports
from rest_framework import serializers

# Project Imports
from src.department.models import (
    Department,
    DepartmentSocialMedia,
    StaffMember,
    AcademicProgram,
    DepartmentDownload,
    DepartmentEvent,
    DepartmentEventGallery,
    DepartmentPlanAndPolicy,
)


class PublicDepartmentSocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentSocialMedia
        fields = ["platform", "url"]


class PublicDepartmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "slug", "short_name", "brief_description", "thumbnail"]


class PublicDepartmentDetailSerializer(serializers.ModelSerializer):
    social_links = PublicDepartmentSocialLinkSerializer(many=True)

    class Meta:
        model = Department
        fields = [
            "id",
            "name",
            "slug",
            "short_name",
            "brief_description",
            "detailed_description",
            "phone_no",
            "email",
            "thumbnail",
            "social_links",
        ]


class PublicStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffMember
        fields = [
            "id",
            "title",
            "name",
            "designation",
            "photo",
            "phone_number",
            "email",
            "message",
            "display_order",
        ]


class PublicProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicProgram
        fields = [
            "id",
            "name",
            "short_name",
            "slug",
            "description",
            "program_type",
            "thumbnail",
        ]


class PublicDownloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentDownload
        fields = ["id", "title", "description", "file"]


class PublicPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentPlanAndPolicy
        fields = ["id", "title", "description", "file"]


class PublicEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentEvent
        fields = [
            "id",
            "title",
            "description_short",
            "event_type",
            "event_start_date",
            "event_end_date",
            "thumbnail",
        ]


class PublicEventGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentEventGallery
        fields = ["id", "image", "caption"]
