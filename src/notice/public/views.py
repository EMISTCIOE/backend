import django_filters
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django_filters.filterset import FilterSet
from django_filters.rest_framework import DjangoFilterBackend

# Rest Framework Imports
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# Project Imports
from src.department.models import Department
from src.notice.constants import NoticeStatus
from src.notice.models import Notice, NoticeCategory
from src.notice.public.messages import SUCCESS_MESSAGE
from src.notice.public.serializers import (
    PublicCategoryForNoticeListSerializer,
    PublicDepartmentForNoticeListSerializer,
    PublicNoticeListSerializer,
)


class PublicNoticeCategoryListAPIView(generics.ListAPIView):
    """API view to list notices categories."""

    permission_classes = [AllowAny]
    queryset = NoticeCategory.objects.filter(is_active=True)
    serializer_class = PublicCategoryForNoticeListSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_fields = ["uuid"]
    search_fields = ["name"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]


class PublicNoticeDepartmentListAPIView(generics.ListAPIView):
    """API view to list notices departments."""

    permission_classes = [AllowAny]
    queryset = Department.objects.filter(is_active=True)
    serializer_class = PublicDepartmentForNoticeListSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_fields = ["uuid"]
    search_fields = ["name"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]


class FilterForPublicNoticeListAPIView(FilterSet):
    department = django_filters.UUIDFilter(
        field_name="department__uuid",
        label="Department",
    )
    category = django_filters.UUIDFilter(field_name="category__uuid", label="Category")

    class Meta:
        model = Notice
        fields = ["uuid", "department", "is_featured", "category"]


class PublicNoticeListAPIView(generics.ListAPIView):
    """API view to list notices."""

    permission_classes = [AllowAny]
    serializer_class = PublicNoticeListSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filterset_class = FilterForPublicNoticeListAPIView
    search_fields = ["title"]
    ordering_fields = ["published_at"]
    ordering = ["-published_at"]

    def get_queryset(self):
        return Notice.objects.filter(is_active=True, status=NoticeStatus.APPROVED.value)


class PublicNoticeRetrieveAPIView(generics.RetrieveAPIView):
    """API view to retrieve notice."""

    permission_classes = [AllowAny]
    serializer_class = PublicNoticeListSerializer

    def get_object(self) -> Notice:
        notice_id = self.kwargs.get("notice_id")
        return get_object_or_404(
            Notice,
            uuid=notice_id,
            is_active=True,
            status=NoticeStatus.APPROVED.value,
        )


class PublicNoticeSetViewedAPIView(generics.UpdateAPIView):
    """API to increase the views count of a notice when viewed"""

    queryset = Notice.objects.filter(is_active=True, status=NoticeStatus.APPROVED.value)
    permission_classes = [AllowAny]
    http_method_names = ["patch"]

    def patch(self, request, *args, **kwargs):
        notice = get_object_or_404(self.queryset, uuid=kwargs["notice_id"])
        notice.set_viewed()
        return Response(
            {"internal": True, "message": SUCCESS_MESSAGE, "views": notice.views},
            status=status.HTTP_200_OK,
        )


class PublicNoticeSetSharedAPIView(generics.UpdateAPIView):
    """API to increase the share count of a notice when shared"""

    queryset = Notice.objects.filter(
        is_active=True,
        status=NoticeStatus.APPROVED.value,
    )
    permission_classes = [AllowAny]
    http_method_names = ["patch"]

    def patch(self, request, *args, **kwargs):
        notice = get_object_or_404(self.queryset, uuid=kwargs["notice_id"])
        notice.set_shared()
        return Response(
            {"internal": True, "message": SUCCESS_MESSAGE, "shares": notice.shares},
            status=status.HTTP_200_OK,
        )
