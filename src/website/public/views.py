# Rest Framework Imports
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# Project Imports
from src.website.models import (
    AcademicCalendar,
    CampusDownload,
    CampusEvent,
    CampusInfo,
    CampusKeyOfficial,
    CampusReport,
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
    filter_fields = ["uuid"]


class PublicCampusEventListAPIView(ListAPIView):
    """Campus Event List API"""

    permission_classes = [AllowAny]
    queryset = CampusEvent.objects.filter(is_active=True)
    serializer_class = PublicCampusEventListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ["-created_at"]
    ordering_fields = ["event_start_date", "created_at"]
    search_fields = ["title"]
    filter_fields = ["event_type", "event_start_date", "event_end_date"]


class PublicCampusEventRetrieveAPIView(RetrieveAPIView):
    """Specific Campus Event API"""

    permission_classes = [AllowAny]
    queryset = CampusEvent.objects.filter(is_active=True)
    serializer_class = PublicCampusEventRetrieveSerializer
    lookup_field = "uuid"


class PublicCampusKeyOfficialListAPIView(ListAPIView):
    """Campus Key Officials List API"""

    permission_classes = [AllowAny]
    serializer_class = PublicCampusKeyOfficialSerializer
    queryset = CampusKeyOfficial.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ["display_order"]
    search_fields = ["full_name"]
    ordering_fields = ["display_order", "created_at"]
    filter_fields = ["uuid", "designation"]


class PublicCampusAcademicCalenderListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PublicAcademicCalendarListSerializer
    queryset = AcademicCalendar.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ["start_year"]
    ordering_fields = ["start_year", "end_year"]
    filter_fields = ["uuid", "program_type", "start_year", "end_year"]


class PublicCampusReportListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PublicCampusReportListSerializer
    queryset = CampusReport.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ["published_date"]
    ordering_fields = ["published_date"]
    filter_fields = ["uuid", "report_type", "published_date", "fiscal_session"]


class PublicCampusFeedbackCreateAPIView(CreateAPIView):
    """Campus Feedback Submission API"""

    permission_classes = [AllowAny]
    serializer_class = PublicCampusFeedbackSerializer
