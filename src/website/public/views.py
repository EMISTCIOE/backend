from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from src.website.models import CampusInfo
from src.website.serializer import CampusInfoPublicSerializer


class CampusInfoPublicView(RetrieveAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        campus = CampusInfo.objects.first()
        if not campus:
            return Response(
                {"detail": "Campus info not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = CampusInfoPublicSerializer(campus)
        return Response(serializer.data, status=status.HTTP_200_OK)
