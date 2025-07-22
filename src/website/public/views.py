# Rest Framework Imports
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# Project Imports
from src.website.models import CampusInfo, CampusDownload
from src.website.public.messages import CAMPUS_INFO_NOT_FOUND
from .serializer import PublicCampusInfoSerializer, PublicCampusDownloadSerializer


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

    serializer_class = PublicCampusDownloadSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return CampusDownload.objects.filter(is_active=True)
