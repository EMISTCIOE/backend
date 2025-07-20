from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

# Project Imports
from src.department.models import Department
from src.notice.models import Notice, NoticeCategory, NoticeMedia
from src.user.models import User


class PublicNoticeMediaSerializerForNoticeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoticeMedia
        fields = ["uuid", "file", "caption", "media_type"]


class PublicDepartmentForNoticeSerializerListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ["uuid", "name"] 


class PublicCategoryForNoticeSerializerListSerializer(serializers.ModelSerializer):

    class Meta:
        model = NoticeCategory
        fields = ["uuid", "name"]


class PublicUserForNoticeListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name")

    class Meta:
        model = User
        fields = ["uuid", "full_name", "photo"]


class PublicNoticeListSerializer(serializers.ModelSerializer):
    department = PublicDepartmentForNoticeSerializerListSerializer()
    category = PublicCategoryForNoticeSerializerListSerializer()
    medias = PublicNoticeMediaSerializerForNoticeListSerializer(many=True)
    author = PublicUserForNoticeListSerializer(source="created_by")

    class Meta:
        model = Notice
        fields = [
            "uuid",
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
