from rest_framework import serializers

from src.department.models import Department
from src.notice.models import NoticeCategory

# Project Imports
from src.user.models import User


class DepartmentForNoticeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name"]


class CategoryForNoticeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoticeCategory
        fields = ["id", "name"]


class UserForNoticeListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name")

    class Meta:
        model = User
        fields = ["id", "full_name", "photo"]
