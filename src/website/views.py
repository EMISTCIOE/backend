from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import CampusInfo
from .serializers import (
    CampusInfoCreateSerializer,
    CampusInfoListSerializer,
    CampusInfoRetrieveSerializer,
)
from .permissions import CampusInfoPermission

class CampusInfoViewSet(viewsets.ModelViewSet):
    queryset = CampusInfo.objects.filter(is_active=True, is_archived=False)
    permission_classes = [CampusInfoPermission]
    http_method_names = ["get", "post"]

    def get_serializer_class(self):
        if self.action == 'list':
            return CampusInfoListSerializer
        if self.action == 'retrieve':
            return CampusInfoRetrieveSerializer
        if self.action == 'create':
            return CampusInfoCreateSerializer
        return CampusInfoListSerializer

    def create(self, request, *args, **kwargs):
        if CampusInfo.objects.filter(is_active=True, is_archived=False).exists():
            return Response(
                {"detail": "CampusInfo already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

