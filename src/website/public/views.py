# Rest Framework Imports
import django_filters
from django_filters.filterset import FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, GenericAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

# Project Imports
from src.website.models import (
    AcademicCalendar,
    CampusDownload,
    CampusEvent,
    CampusInfo,
    CampusKeyOfficial,
    CampusSection,
    CampusUnit,
    CampusReport,
    CampusUnion,
    StudentClub,
    StudentClubEvent,
)
from src.website.public.messages import CAMPUS_INFO_NOT_FOUND
from src.website.utils import build_global_gallery_items

from .serializer import (
    PublicAcademicCalendarListSerializer,
    PublicCampusDownloadSerializer,
    PublicCampusEventListSerializer,
    PublicCampusEventRetrieveSerializer,
    PublicCampusFeedbackSerializer,
    PublicCampusInfoSerializer,
    PublicCampusKeyOfficialSerializer,
    PublicCampusReportListSerializer,
    PublicCampusSectionListSerializer,
    PublicCampusSectionRetrieveSerializer,
    PublicCampusUnitListSerializer,
    PublicCampusUnitRetrieveSerializer,
    PublicCampusUnionListSerializer,
    PublicCampusUnionRetrieveSerializer,
    PublicStudentClubEventListSerializer,
    PublicStudentClubEventRetrieveSerializer,
    PublicStudentClubListSerializer,
    PublicStudentClubRetrieveSerializer,
    PublicGlobalGallerySerializer,
)


class PublicCampusInfoRetrieveAPIView(RetrieveAPIView):
    """Campus Information API"""

    permission_classes = [AllowAny]
    serializer_class = PublicCampusInfoSerializer

    def get(self, request):
        campus = CampusInfo.objects.filter(is_active=True).first()
        if not campus:
            return Response(
                {"detail": CAMPUS_INFO_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(campus, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class PublicCampusDownloadListAPIView(ListAPIView):
    """Campus Download Listing API"""

    permission_classes = [AllowAny]
    serializer_class = PublicCampusDownloadSerializer
    queryset = CampusDownload.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ["-created_at"]
    filterset_fields = ["uuid"]


class PublicCampusEventViewSet(ReadOnlyModelViewSet):
    """
    Public API for listing and retrieving campus events with galleries.
    """

    permission_classes = [AllowAny]
    queryset = CampusEvent.objects.filter(is_active=True)
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_fields = ["event_type", "event_start_date", "event_end_date"]
    search_fields = ["title"]
    ordering = ["-created_at"]
    ordering_fields = ["event_start_date", "created_at"]
    http_method_names = ["get", "head", "options"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return (
                PublicCampusEventListSerializer
                if self.action == "list"
                else PublicCampusEventRetrieveSerializer
            )


class PublicCampusKeyOfficialFilterSet(FilterSet):
    designation = django_filters.CharFilter(
        field_name="designation__code", lookup_expr="iexact"
    )
    is_key_official = django_filters.BooleanFilter()

    class Meta:
        model = CampusKeyOfficial
        fields = ["designation", "is_key_official"]


class PublicCampusKeyOfficialListAPIView(ListAPIView):
    """Campus Staff List API"""

    permission_classes = [AllowAny]
    serializer_class = PublicCampusKeyOfficialSerializer
    queryset = CampusKeyOfficial.objects.filter(is_active=True).select_related(
        "designation"
    )
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ["display_order"]
    search_fields = ["full_name", "designation__title"]
    ordering_fields = ["display_order", "created_at"]
    filterset_class = PublicCampusKeyOfficialFilterSet


class PublicCampusAcademicCalenderListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PublicAcademicCalendarListSerializer
    queryset = AcademicCalendar.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ["start_year"]
    ordering_fields = ["start_year", "end_year"]
    filterset_fields = ["uuid", "program_type", "start_year", "end_year"]


class PublicCampusReportListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PublicCampusReportListSerializer
    queryset = CampusReport.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ["published_date"]
    ordering_fields = ["published_date"]
    filterset_fields = ["uuid", "report_type", "published_date", "fiscal_session"]


class PublicCampusFeedbackCreateAPIView(CreateAPIView):
    """Campus Feedback Submission API"""

    permission_classes = [AllowAny]
    serializer_class = PublicCampusFeedbackSerializer


class PublicCampusUnionReadOnlyViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = CampusUnion.objects.filter(is_active=True)
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_fields = ["name"]
    search_fields = ["name"]
    ordering_fields = ["-created_at", "name"]
    http_method_names = ["get", "head", "options"]
    lookup_field = "uuid"
    lookup_url_kwarg = "uuid"

    def get_serializer_class(self):
        if self.request.method == "GET":
            return (
                PublicCampusUnionListSerializer
                if self.action == "list"
                else PublicCampusUnionRetrieveSerializer
            )


class PublicCampusSectionReadOnlyViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = CampusSection.objects.filter(is_active=True)
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_fields = ["slug", "name"]
    search_fields = ["name", "short_description"]
    ordering_fields = ["display_order", "-created_at"]
    http_method_names = ["get", "head", "options"]
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    def get_serializer_class(self):
        if self.request.method == "GET":
            return (
                PublicCampusSectionListSerializer
                if self.action == "list"
                else PublicCampusSectionRetrieveSerializer
            )


class PublicCampusUnitReadOnlyViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = CampusUnit.objects.filter(is_active=True)
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_fields = ["slug", "name"]
    search_fields = ["name", "short_description"]
    ordering_fields = ["display_order", "-created_at"]
    http_method_names = ["get", "head", "options"]
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    def get_serializer_class(self):
        if self.request.method == "GET":
            return (
                PublicCampusUnitListSerializer
                if self.action == "list"
                else PublicCampusUnitRetrieveSerializer
            )


class PublicStudentClubReadOnlyViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    queryset = StudentClub.objects.filter(is_active=True)
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_fields = ["name"]
    search_fields = ["name"]
    ordering_fields = ["-created_at", "name"]
    http_method_names = ["get", "head", "options"]
    lookup_field = "uuid"
    lookup_url_kwarg = "uuid"

    def get_serializer_class(self):
        if self.request.method == "GET":
            return (
                PublicStudentClubListSerializer
                if self.action == "list"
                else PublicStudentClubRetrieveSerializer
            )


class PublicStudentClubEventFilter(FilterSet):
    club = django_filters.UUIDFilter(field_name="club.uuid", label="Club")

    class Meta:
        model = StudentClubEvent
        fields = ["club", "date"]


class PublicStudentClubEventViewSet(ReadOnlyModelViewSet):
    """
    Public API for listing and retrieving student club events with galleries.
    """

    permission_classes = [AllowAny]
    queryset = StudentClubEvent.objects.filter(is_active=True)
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_class = PublicStudentClubEventFilter
    search_fields = ["title", "description"]
    ordering_fields = ["-created_at", "title", "date"]
    http_method_names = ["get", "head", "options"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return (
                PublicStudentClubEventListSerializer
                if self.action == "list"
                else PublicStudentClubEventRetrieveSerializer
            )


class PublicGlobalGalleryPagination(LimitOffsetPagination):
    default_limit = 24
    max_limit = 120


class PublicGlobalGalleryListAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PublicGlobalGallerySerializer
    pagination_class = PublicGlobalGalleryPagination

    def get(self, request, *args, **kwargs):
        items = build_global_gallery_items()
        source_type = request.query_params.get("source_type")
        if source_type:
            items = [item for item in items if item["source_type"] == source_type]

        search = request.query_params.get("search", "")
        if search:
            search_lower = search.lower()
            items = [
                item
                for item in items
                if search_lower in (item.get("source_name") or "").lower()
                or search_lower in (item.get("caption") or "").lower()
                or search_lower in (item.get("source_context") or "").lower()
            ]

        items.sort(key=lambda item: item["created_at"], reverse=True)
        page = self.paginate_queryset(items, request, view=self)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
