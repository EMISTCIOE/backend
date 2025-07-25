# Rest Framework Imports
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# Project Imports
from src.website.models import (
    CampusDownload,
    CampusEvent,
    CampusInfo,
    CampusKeyOfficial,
    CampusReport,
)
from src.website.public.messages import CAMPUS_INFO_NOT_FOUND

from .serializer import (
    PublicCampusDownloadSerializer,
    PublicCampusEventListSerializer,
    PublicCampusEventRetrieveSerializer,
    PublicCampusFeedbackSerializer,
    PublicCampusInfoSerializer,
    PublicCampusKeyOfficialSerializer,
    PublicCampusReportSerializer,
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


class PublicCampusEventListAPIView(ListAPIView):
    """Campus Event List API"""

    permission_classes = [AllowAny]
    queryset = CampusEvent.objects.filter(is_active=True)
    serializer_class = PublicCampusEventListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ["-created_at"]
    filter_fields = ["event_type"]


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
    ordering_fields = ["display_order", "created_at"]
    filter_fields = ["designation"]


class PublicCampusFeedbackCreateAPIView(CreateAPIView):
    """Campus Feedback Submission API"""

    permission_classes = [AllowAny]
    serializer_class = PublicCampusFeedbackSerializer


class PublicCampusReportListAPIView(ListAPIView):
    """Campus Report List API"""

    permission_classes = [AllowAny]
    serializer_class = PublicCampusReportSerializer
    queryset = CampusReport.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering = ["-published_date"]
    ordering_fields = ["published_date", "created_at"]
    filter_fields = ["report_type"]
