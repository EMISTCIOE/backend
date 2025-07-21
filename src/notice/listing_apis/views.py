from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView

# Project Imports
from src.department.models import Department
from src.notice.listing_apis.serializers import (
    CategoryForNoticeListSerializer,
    DepartmentForNoticeListSerializer,
    UserForNoticeListSerializer,
)
from src.notice.models import NoticeCategory
from src.user.models import User
from src.user.permissions import UserSetupPermission


class DepartmentForNoticeListAPIView(ListAPIView):
    permission_classes = [UserSetupPermission]
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentForNoticeListSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_fields = ["id", "name"]
    search_fields = ["id", "name"]
    ordering_fields = ["id", "name"]
    ordering = ["name"]


class CategoryForNoticeListAPIView(ListAPIView):
    permission_classes = [UserSetupPermission]
    queryset = NoticeCategory.objects.filter(is_active=True)
    serializer_class = CategoryForNoticeListSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_fields = ["id", "name"]
    search_fields = ["id", "name"]
    ordering_fields = ["id", "name"]
    ordering = ["name"]


class AuthorForNoticeListAPIView(ListAPIView):
    permission_classes = [UserSetupPermission]
    serializer_class = UserForNoticeListSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_fields = ["id", "email"]
    search_fields = ["id", "email"]
    ordering_fields = ["id", "email"]
    ordering = ["-id"]

    def get_queryset(self):
        return User.objects.filter(is_active=True)
