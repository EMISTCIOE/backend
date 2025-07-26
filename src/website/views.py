from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

# Project Imports
from src.website.messages import (
    CAMPUS_INFO_NOT_FOUND,
    SOCIAL_MEDIA_DELETED_SUCCESS,
    SOCIAL_MEDIA_NOT_FOUND,
)
from .models import (
    CampusInfo,
    CampusKeyOfficial,
    SocialMediaLink,
    CampusReport,
    CampusEvent,
)

from .serializers import (
    CampusInfoPatchSerializer,
    CampusInfoRetrieveSerializer,
    CampusKeyOfficialCreateSerializer,
    CampusKeyOfficialListSerializer,
    CampusKeyOfficialPatchSerializer,
    CampusKeyOfficialRetrieveSerializer,
    CampusReportListSerializer,
    CampusReportRetrieveSerializer,
    CampusReportCreateSerializer,
    CampusReportPatchSerializer,
    CampusEventListSerializer,
    CampusEventRetrieveSerializer,
    CampusEventCreateSerializer,
    CampusEventPatchSerializer,
)

from .permissions import (
    CampusReportPermission,
    CampusEventPermission,
    CampusInfoPermission,
    CampusKeyOfficialPermission,
)


class CampusReportViewSet(viewsets.ModelViewSet):
    """Campus Report API"""

    permission_classes = [CampusReportPermission]
    queryset = CampusReport.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["report_type", "fiscal_session", "is_active"]
    search_fields = ["report_type"]
    ordering_fields = ["published_date", "created_at"]
    ordering = ["-created_at"]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.action == "list":
            return CampusReportListSerializer
        elif self.action == "retrieve":
            return CampusReportRetrieveSerializer
        elif self.action == "create":
            return CampusReportCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return CampusReportPatchSerializer
        return CampusReportListSerializer

    def perform_destroy(self, instance):
        if instance.file:
            instance.file.delete(save=False)
        instance.delete()


class CampusEventViewSet(viewsets.ModelViewSet):
    """Campus Event API"""

    permission_classes = [CampusEventPermission]
    queryset = CampusEvent.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["event_type", "is_active"]
    search_fields = ["title", "description_short", "description_detailed"]
    ordering_fields = ["event_start_date", "created_at"]
    ordering = ["-created_at"]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.action == "list":
            return CampusEventListSerializer
        elif self.action == "retrieve":
            return CampusEventRetrieveSerializer
        elif self.action == "create":
            return CampusEventCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return CampusEventPatchSerializer
        return CampusEventListSerializer

    @transaction.atomic
    def perform_destroy(self, instance):
        # Delete thumbnail file
        if instance.thumbnail:
            instance.thumbnail.delete(save=False)
        # Delete all gallery images
        for gallery in instance.gallery.all():
            if gallery.image:
                gallery.image.delete(save=False)
            gallery.delete()
        instance.delete()

    @transaction.atomic
    def perform_update(self, serializer):
        instance = self.get_object()
        old_thumb = instance.thumbnail
        new_thumb = self.request.FILES.get("thumbnail")
        if old_thumb and new_thumb and old_thumb != new_thumb:
            old_thumb.delete(save=False)
        serializer.save()


class CampusInfoAPIView(generics.GenericAPIView):
    """Campus Info Retrive and Update APIs"""

    permission_classes = [CampusInfoPermission]
    serializer_class = CampusInfoRetrieveSerializer

    def get_object(self):
        return CampusInfo.objects.filter(is_archived=False).first()

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response(
                {"detail": CAMPUS_INFO_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.get_serializer(instance, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response(
                {"detail": CAMPUS_INFO_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = CampusInfoPatchSerializer(
            instance,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class SocialMediaLinkDeleteAPIView(APIView):
    permission_classes = [CampusInfoPermission]

    def delete(self, request, pk):
        try:
            link = SocialMediaLink.objects.get(pk=pk)
        except SocialMediaLink.DoesNotExist:
            return Response(
                {"detail": SOCIAL_MEDIA_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        link.delete()
        return Response(
            {"message": SOCIAL_MEDIA_DELETED_SUCCESS},
            status=status.HTTP_204_NO_CONTENT,
        )


class CampusKeyOfficialViewSet(viewsets.ModelViewSet):
    """Campus Key Officials CRUD APIs"""

    permission_classes = [CampusKeyOfficialPermission]
    queryset = CampusKeyOfficial.objects.filter(is_archived=False)
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ["full_name", "designation", "email"]
    ordering_fields = ["full_name", "created_at", "display_order"]
    ordering = ["display_order", "-created_at"]
    filterset_fields = ["designation", "is_active"]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            if self.action == "list":
                return CampusKeyOfficialListSerializer
            else:
                return CampusKeyOfficialRetrieveSerializer
        elif self.request.method == "POST":
            return CampusKeyOfficialCreateSerializer
        elif self.request.method == "PATCH":
            return CampusKeyOfficialPatchSerializer

        return CampusKeyOfficialListSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Delete associated file if exists
        if instance.photo:
            instance.photo.delete(save=False)

        return super().destroy(request, *args, **kwargs)
