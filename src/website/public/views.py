# Rest Framework Imports
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


# Project Imports
from src.website.models import CampusInfo
from src.website.serializer import PublicCampusInfoSerializer
from src.website.public.messages import CAMPUS_INFO_NOT_FOUND


class PublicCampusInfoRetrieveAPIView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = PublicCampusInfoSerializer

    def get(self, request, *args, **kwargs):
        campus = CampusInfo.objects.first()
        if not campus:
            return Response(
                {"detail": "Campus info not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = self.serializer_class(campus)
        return Response(serializer.data, status=status.HTTP_200_OK)
