from rest_framework import generics, status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from src.website.messages import CAMPUS_INFO_NOT_FOUND, ONLY_ONE_CAMPUS_INFO_ALLOWED

# Project Imports
from .models import CampusInfo, CampusKeyOfficial
from .permissions import CampusInfoPermission
from .serializers import (
    CampusInfoCreateSerializer,
    CampusInfoRetrieveSerializer,
    CampusKeyOfficialCreateSerializer,
    CampusKeyOfficialListSerializer,
    CampusKeyOfficialPatchSerializer,
    CampusKeyOfficialRetrieveSerializer,
)


class CampusInfoAPIView(generics.GenericAPIView):
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

    def post(self, request, *args, **kwargs):
        if CampusInfo.objects.filter(is_active=True, is_archived=False).exists():
            return Response(
                {"detail": ONLY_ONE_CAMPUS_INFO_ALLOWED},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = CampusInfoCreateSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response(
                {"detail": CAMPUS_INFO_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = CampusInfoCreateSerializer(
            instance,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CampusKeyOfficialViewSet(viewsets.ModelViewSet):
    queryset = CampusKeyOfficial.objects.filter(is_archived=False)
    permission_classes = [CampusInfoPermission]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["full_name"]
    ordering_fields = ["full_name", "created_at"]
    ordering = ["-created_at"]

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
