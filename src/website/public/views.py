# Rest Framework Imports
import django_filters
from django_filters.filterset import FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
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
    CampusReport,
    CampusUnion,
    StudentClub,
    StudentClubEvent,
)
from src.website.public.messages import CAMPUS_INFO_NOT_FOUND

from .serializer import (
    PublicAcademicCalendarListSerializer,
    PublicCampusDownloadSerializer,
    PublicCampusEventListSerializer,
    PublicCampusEventRetrieveSerializer,
    PublicCampusFeedbackSerializer,
    PublicCampusInfoSerializer,
    PublicCampusKeyOfficialSerializer,
    PublicCampusReportListSerializer,
    PublicCampusUnionListSerializer,
    PublicCampusUnionRetrieveSerializer,
    PublicContactInquirySerializer,
    PublicStudentClubEventListSerializer,
    PublicStudentClubEventRetrieveSerializer,
    PublicStudentClubListSerializer,
    PublicStudentClubRetrieveSerializer,
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


class PublicCampusKeyOfficialListAPIView(ListAPIView):
    """Campus Key Officials List API"""

    permission_classes = [AllowAny]
    serializer_class = PublicCampusKeyOfficialSerializer
    queryset = CampusKeyOfficial.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ["display_order"]
    search_fields = ["full_name"]
    ordering_fields = ["display_order", "created_at"]
    filterset_fields = ["uuid", "designation"]


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


class PublicContactInquiryCreateAPIView(CreateAPIView):
    """Campus Contact Inquiry Create API"""

    permission_classes = [AllowAny]
    serializer_class = PublicContactInquirySerializer
