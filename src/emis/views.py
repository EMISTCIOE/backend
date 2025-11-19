"""
EMIS API viewsets for VPS info, hardware inventory, and email reset requests.
"""

from rest_framework import mixins, viewsets

from src.user.permissions import IsEMISStaff

from .models import EmailResetRequest, EMISHardware, EMISVPSInfo
from .serializers import (
    EmailResetRequestSerializer,
    EMISHardwareSerializer,
    EMISVPSInfoSerializer,
)


class EMISVPSInfoViewSet(viewsets.ModelViewSet):
    queryset = EMISVPSInfo.objects.filter(is_active=True).order_by("vps_label")
    serializer_class = EMISVPSInfoSerializer
    permission_classes = [IsEMISStaff]


class EMISHardwareViewSet(viewsets.ModelViewSet):
    queryset = EMISHardware.objects.filter(is_active=True).order_by("name")
    serializer_class = EMISHardwareSerializer
    permission_classes = [IsEMISStaff]


class EmailResetRequestViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = EmailResetRequest.objects.filter(is_active=True).order_by("-created_at")
    serializer_class = EmailResetRequestSerializer
    permission_classes = [IsEMISStaff]
