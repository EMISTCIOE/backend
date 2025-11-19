"""
EMIS Views
"""

from django.db import models
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from src.libs.pagination import CustomPagination
from src.user.permissions import IsEMISStaff

from .models import VPSConfiguration
from .serializers import (
    OTPRequestSerializer,
    OTPVerifySerializer,
    VPSConfigurationCreateSerializer,
    VPSConfigurationDetailSerializer,
    VPSConfigurationListSerializer,
    VPSConfigurationUpdateSerializer,
)


class VPSConfigurationViewSet(viewsets.ModelViewSet):
    """
    VPS Configuration ViewSet
    - Only accessible by EMIS Staff
    - Password viewing requires OTP verification
    """

    queryset = VPSConfiguration.objects.filter(is_active=True).order_by("label")
    pagination_class = CustomPagination
    permission_classes = [IsEMISStaff]

    def get_serializer_class(self):
        if self.action == "create":
            return VPSConfigurationCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return VPSConfigurationUpdateSerializer
        elif self.action == "retrieve":
            return VPSConfigurationDetailSerializer
        elif self.action == "request_otp":
            return OTPRequestSerializer
        elif self.action == "verify_otp":
            return OTPVerifySerializer
        return VPSConfigurationListSerializer

    def list(self, request, *args, **kwargs):
        """List all VPS configurations"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Search by label or IP
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                models.Q(label__icontains=search) | models.Q(ip_address__icontains=search),
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Create new VPS configuration"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Update VPS configuration"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Soft delete VPS configuration"""
        instance = self.get_object()
        instance.is_active = False
        instance.updated_by = request.user
        instance.save()
        return Response(
            {"message": f"VPS configuration '{instance.label}' has been deactivated."},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="request-otp")
    def request_otp(self, request):
        """Request OTP for viewing password"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="verify-otp")
    def verify_otp(self, request):
        """Verify OTP and get password"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="access-history")
    def access_history(self, request, pk=None):
        """Get access history for VPS"""
        vps_config = self.get_object()
        otp_verifications = vps_config.otp_verifications.filter(
            is_used=True,
        ).select_related("user").order_by("-used_at")[:20]

        history = [
            {
                "user": otp.user.get_full_name(),
                "accessed_at": otp.used_at,
            }
            for otp in otp_verifications
        ]

        return Response({
            "vps_label": vps_config.label,
            "total_accesses": vps_config.access_count,
            "recent_history": history,
        })
