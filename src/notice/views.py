# Django Imports
import django_filters
from django.core.files.storage import default_storage
from django.db import transaction
from django_filters.filterset import FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

# Rest Framework Imports
from rest_framework.viewsets import ModelViewSet

# Project Imports
from src.libs.utils import set_binary_files_null_if_empty

from .messages import MEDIA_DELETED_SUCCESS, MEDIA_NOT_FOUND, NOTICE_DELETED_SUCCESS
from .models import Notice, NoticeMedia
from .permissions import NoticePermission,NoticeStatusUpdatePermission
from .serializers import (
    NoticeCreateSerializer,
    NoticeListSerializer,
    NoticePatchSerializer,
    NoticeRetrieveSerializer,
    NoticeStatusUpdateSerializer,
)


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
    http_method_names = ["options", "head", "get", "patch", "delete", "post"]

    def get_queryset(self):
        return Notice.objects.filter(is_archived=False)

    def get_serializer_class(self):
        serializer_class = None

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

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        Delete the notice along with all associated
        media files from storage and database.
        """

        instance = self.get_object()
        medias = instance.medias.all()

        # Delete associated media files from disk
        for media in medias:
            if media.file and default_storage.exists(media.file.name):
                default_storage.delete(media.file.name)
            media.delete()

        # Delete thumbnail if exists
        if instance.thumbnail and default_storage.exists(instance.thumbnail.name):
            default_storage.delete(instance.thumbnail.name)

        instance.delete()

        return Response({"detail": NOTICE_DELETED_SUCCESS}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['patch','put'],
        url_path='update-status',
        permission_classes=[NoticeStatusUpdatePermission],
        serializer_class=NoticeStatusUpdateSerializer
    )
    def update_status(self, request, pk=None):
        """Update notice status: PENDING ↔ APPROVED/REJECTED."""
        notice = self.get_object()
        serializer = self.get_serializer(notice, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Status updated successfully',
                'status': serializer.data['status'],
                'updated_at': serializer.data['updated_at'],
                'updated_by': request.user.username
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["delete"],
        url_path="media/(?P<media_id>[^/.]+)",
        name="Delete Notice Media",
    )
    def delete_media(self, request, pk=None, media_id=None):
        """
        Delete a media file associated with a specific notice.
        """
        notice = self.get_object()

        try:
            media = notice.medias.get(id=media_id, is_active=True)
        except NoticeMedia.DoesNotExist:
            return Response(
                {"detail": MEDIA_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        if media.file and default_storage.exists(media.file.name):
            default_storage.delete(media.file.name)

        media.delete()

        return Response(
            {"detail": MEDIA_DELETED_SUCCESS},
            status=status.HTTP_204_NO_CONTENT,
        )
