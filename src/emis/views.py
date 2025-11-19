"""
EMIS API viewsets for VPS info, hardware inventory, and email reset requests.
"""

import logging
from django.utils import timezone
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from src.user.permissions import IsEMISStaff

from .models import EmailResetRequest, EMISHardware, EMISVPSInfo, EMISVPSService, RequestStatus
from .serializers import (
    EmailResetRequestSerializer,
    EMISHardwareSerializer,
    EMISVPSInfoSerializer,
    EMISVPSServiceSerializer,
)
from .webhook_utils import call_email_reset_webhook

logger = logging.getLogger(__name__)


class EMISVPSInfoViewSet(viewsets.ModelViewSet):
    queryset = EMISVPSInfo.objects.filter(is_active=True).order_by("vps_name")
    serializer_class = EMISVPSInfoSerializer
    permission_classes = [IsEMISStaff]


class EMISVPSServiceViewSet(viewsets.ModelViewSet):
    serializer_class = EMISVPSServiceSerializer
    permission_classes = [IsEMISStaff]

    def get_queryset(self):
        return EMISVPSService.objects.filter(is_active=True).order_by("vps", "port")


class EMISHardwareViewSet(viewsets.ModelViewSet):
    queryset = EMISHardware.objects.filter(is_active=True).order_by("name")
    serializer_class = EMISHardwareSerializer
    permission_classes = [IsEMISStaff]


class EmailResetRequestViewSet(viewsets.ModelViewSet):
    queryset = EmailResetRequest.objects.filter(is_active=True).order_by("-created_at")
    serializer_class = EmailResetRequestSerializer
    permission_classes = [IsEMISStaff]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve an email reset request."""
        reset_request = self.get_object()
        
        if reset_request.status != RequestStatus.PENDING:
            return Response(
                {"detail": "Request has already been processed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reset_request.status = RequestStatus.APPROVED
        reset_request.processed_at = timezone.now()
        reset_request.processed_by = request.user
        reset_request.notes = request.data.get("notes", "")
        reset_request.save()
        
        # Call webhook for approved email reset request
        webhook_success = call_email_reset_webhook(
            action="approve",
            primary_email=reset_request.primary_email,
            secondary_email=reset_request.secondary_email,
            request_id=reset_request.id,
            full_name=reset_request.full_name,
            roll_number=reset_request.roll_number,
            phone_number=reset_request.phone_number,
            processed_by_email=request.user.email,
            notes=reset_request.notes
        )
        
        if not webhook_success:
            logger.warning(f"Webhook call failed for approved request {reset_request.id}")
        
        return Response({
            "detail": "Request approved successfully",
            "webhook_called": webhook_success
        })

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject an email reset request."""
        reset_request = self.get_object()
        
        if reset_request.status != RequestStatus.PENDING:
            return Response(
                {"detail": "Request has already been processed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reset_request.status = RequestStatus.REJECTED
        reset_request.processed_at = timezone.now()
        reset_request.processed_by = request.user
        reset_request.notes = request.data.get("notes", "")
        reset_request.save()
        
        # Call webhook for rejected email reset request
        webhook_success = call_email_reset_webhook(
            action="reject",
            primary_email=reset_request.primary_email,
            secondary_email=reset_request.secondary_email,
            request_id=reset_request.id,
            full_name=reset_request.full_name,
            roll_number=reset_request.roll_number,
            phone_number=reset_request.phone_number,
            processed_by_email=request.user.email,
            notes=reset_request.notes
        )
        
        if not webhook_success:
            logger.warning(f"Webhook call failed for rejected request {reset_request.id}")
        
        return Response({
            "detail": "Request rejected successfully", 
            "webhook_called": webhook_success
        })
