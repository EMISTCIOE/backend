from rest_framework import serializers

# Project Imports
from src.department.models import (
    AcademicProgram,
    Department,
    DepartmentDownload,
    DepartmentEvent,
    DepartmentEventGallery,
    DepartmentPlanAndPolicy,
    DepartmentSocialMedia,
)
from src.website.models import CampusKeyOfficial


class PublicDepartmentSocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentSocialMedia
        fields = ["uuid", "platform", "url"]


class PublicDepartmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = [
            "uuid",
            "name",
            "slug",
            "short_name",
            "brief_description",
            "thumbnail",
        ]


class PublicDepartmentDetailSerializer(serializers.ModelSerializer):
    social_links = PublicDepartmentSocialLinkSerializer(many=True)

    class Meta:
        model = Department
        fields = [
            "uuid",
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


class PublicDepartmentStaffSerializer(serializers.ModelSerializer):
    designation = serializers.CharField(source="designation.title", read_only=True)
    title = serializers.CharField(source="title_prefix", read_only=True)
    name = serializers.CharField(source="full_name", read_only=True)

    class Meta:
        model = CampusKeyOfficial
        fields = [
            "uuid",
            "title",
            "name",
            "designation",
            "photo",
            # phone_number intentionally omitted for public endpoints
            "email",
            "message",
            "display_order",
        ]


class PublicDepartmentProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicProgram
        fields = [
            "uuid",
            "name",
            "short_name",
            "slug",
            "description",
            "program_type",
            "thumbnail",
        ]


class PublicDepartmentDownloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentDownload
        fields = ["uuid", "title", "description", "file"]


class PublicDepartmentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentPlanAndPolicy
        fields = ["uuid", "title", "description", "file"]


class PublicDepartmentEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentEvent
        fields = [
            "uuid",
            "title",
            "description_short",
            "event_type",
            "event_start_date",
            "event_end_date",
            "thumbnail",
        ]


class PublicDepartmentEventGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentEventGallery
        fields = ["uuid", "image", "caption"]
