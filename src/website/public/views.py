# Rest Framework Imports
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter

# Project Imports
from src.website.models import (
    CampusInfo,
    CampusDownload,
    CampusEvent,
    CampusKeyOfficial,
)
from src.website.public.messages import CAMPUS_INFO_NOT_FOUND
from .serializer import (
    PublicCampusInfoSerializer,
    PublicCampusDownloadSerializer,
    PublicCampusEventListSerializer,
    PublicCampusEventRetrieveSerializer,
    PublicCampusKeyOfficialSerializer,
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

    queryset = CampusEvent.objects.filter(is_active=True)
    serializer_class = PublicCampusEventRetrieveSerializer
    permission_classes = [AllowAny]
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
