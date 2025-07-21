# Django Imports
import django_filters
from django.db import transaction
from django_filters.filterset import FilterSet
from django_filters.rest_framework import DjangoFilterBackend

# Rest Framework Imports
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter

# Project Imports
from src.libs.utils import set_binary_files_null_if_empty
from .serializers import (
    NoticeCreateSerializer,
    NoticeListSerializer,
    NoticePatchSerializer,
    NoticeRetrieveSerializer,
)
from .models import Notice
from .permissions import NoticePermission


class FilterForNoticeViewSet(FilterSet):
    """Filters For Notice ViewSet"""

    date = django_filters.DateFromToRangeFilter(field_name="created_at")

    class Meta:
        model = Notice
        fields = ["id", "status", "department", "category", "is_featured", "date"]


class NoticeViewSet(ModelViewSet):
    """
    ViewSet for managing CRUD operations for Notice.
    """

    permission_classes = [NoticePermission]
    filterset_class = FilterForNoticeViewSet
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["title"]
    ordering_fields = ["-created_at", "published_at"]
    http_method_names = ["options", "head", "get", "patch", "post"]

    def get_queryset(self):
        return Notice.objects.filter(is_archived=False)

    def get_serializer_class(self):
        serializer_class = NoticeListSerializer
        if self.request.method == "GET":
            if self.action == "list":
                serializer_class = NoticeListSerializer
            else:
                serializer_class = NoticeRetrieveSerializer

        if self.request.method == "POST":
            serializer_class = NoticeCreateSerializer
        elif self.request.method == "PATCH":
            serializer_class = NoticePatchSerializer
        return serializer_class

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # set blank file fields to None/null
        file_fields = ["thumbnail"]
        if file_fields:
            set_binary_files_null_if_empty(file_fields, request.data)
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        # set blank file fields to None/null
        file_fields = ["thumbnail"]
        if file_fields:
            set_binary_files_null_if_empty(file_fields, request.data)
        return super().update(request, *args, **kwargs)
