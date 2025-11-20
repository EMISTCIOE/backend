"""
EMIS API viewsets for VPS info, hardware inventory, and email reset requests.
"""

import logging
from django.utils import timezone
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from src.user.permissions import IsEMISStaff

from .models import (
    EmailResetRequest,
    EMISHardware,
    EMISVPSInfo,
    EMISVPSService,
    EnvironmentType,
    HardwareStatus,
    HealthStatus,
    RequestStatus,
    ServiceStatus,
)
from .serializers import (
    EmailResetRequestSerializer,
    EMISHardwareSerializer,
    EMISVPSInfoSerializer,
    EMISVPSServiceSerializer,
)
from .webhook_utils import call_email_reset_webhook
from src.libs.send_mail import _send_email

logger = logging.getLogger(__name__)


class EMISVPSInfoViewSet(viewsets.ModelViewSet):
    queryset = EMISVPSInfo.objects.filter(is_active=True).order_by("vps_name")
    serializer_class = EMISVPSInfoSerializer
    permission_classes = [IsEMISStaff]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["vps_name", "slug", "ip_address", "private_ip_address", "tags"]
    ordering_fields = ["vps_name", "environment", "health_status", "updated_at"]

    @action(detail=True, methods=["post"], url_path="mark-health")
    def mark_health(self, request, pk=None):
        node = self.get_object()
        status_value = request.data.get("status")
        if status_value not in HealthStatus.values:
            return Response(
                {"detail": "Invalid health status", "allowed": HealthStatus.values},
                status=status.HTTP_400_BAD_REQUEST,
            )
        node.mark_health(status_value)
        return Response({"detail": "Health status updated", "health_status": node.health_status})

    @action(detail=True, methods=["get"], url_path="services")
    def list_services(self, request, pk=None):
        node = self.get_object()
        serializer = EMISVPSServiceSerializer(node.get_services(), many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="bulk-tag")
    def bulk_tag(self, request):
        ids = request.data.get("ids", [])
        tags = request.data.get("tags", [])
        if not isinstance(ids, list) or not isinstance(tags, list):
            return Response({"detail": "ids and tags must be lists"}, status=status.HTTP_400_BAD_REQUEST)
        updated = (
            EMISVPSInfo.objects.filter(id__in=ids, is_active=True)
            .update(tags=tags, updated_at=timezone.now(), updated_by=request.user)
        )
        return Response({"detail": f"Tags updated for {updated} VPS nodes"})


class EMISVPSServiceViewSet(viewsets.ModelViewSet):
    serializer_class = EMISVPSServiceSerializer
    permission_classes = [IsEMISStaff]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "service_key", "domain", "maintained_by"]
    ordering_fields = ["name", "status", "updated_at", "port"]

    def get_queryset(self):
        return EMISVPSService.objects.filter(is_active=True).order_by("vps", "port")

    @action(detail=True, methods=["post"], url_path="deploy")
    def deploy(self, request, pk=None):
        service = self.get_object()
        status_choice = request.data.get("status", ServiceStatus.RUNNING)
        if status_choice not in ServiceStatus.values:
            return Response(
                {"detail": "Invalid status", "allowed": ServiceStatus.values},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service.status = status_choice
        service.version = request.data.get("version", service.version)
        service.last_deployed_at = timezone.now()
        service.updated_by = request.user
        service.save(update_fields=["status", "version", "last_deployed_at", "updated_by", "updated_at"])
        return Response({"detail": "Deployment metadata updated"})


class EMISHardwareViewSet(viewsets.ModelViewSet):
    queryset = EMISHardware.objects.filter(is_active=True).order_by("name")
    serializer_class = EMISHardwareSerializer
    permission_classes = [IsEMISStaff]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "asset_tag", "ip_address", "location", "responsible_team"]
    ordering_fields = ["name", "environment", "status", "updated_at"]

    @action(detail=False, methods=["post"], url_path="bulk-import")
    def bulk_import(self, request):
        assets = request.data.get("assets", [])
        if not isinstance(assets, list):
            return Response({"detail": "assets must be a list"}, status=status.HTTP_400_BAD_REQUEST)
        created = []
        for payload in assets:
            serializer = self.get_serializer(data=payload)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            created.append(serializer.data)
        return Response({"detail": f"Imported {len(created)} assets", "items": created}, status=status.HTTP_201_CREATED)


class EmailResetRequestViewSet(viewsets.ModelViewSet):
    queryset = EmailResetRequest.objects.filter(is_active=True).order_by("-created_at")
    serializer_class = EmailResetRequestSerializer
    
    def create(self, request, *args, **kwargs):
        """Create an email reset request and notify the requester that we've received it."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Save the instance (this will set request_sequence and created_by as in serializer.create)
        instance = serializer.save()

        # Prepare and send notification email (best-effort; don't block the response on failures)
        try:
            from src.libs.send_mail import send_email_reset_received_notification
            
            # Use the enhanced email reset received notification
            email_sent = send_email_reset_received_notification(
                full_name=instance.full_name,
                college_email=instance.primary_email,
                secondary_email=instance.secondary_email,
                request_sequence=instance.request_sequence,
                submitted_at=instance.created_at,
                request=request
            )
            
            if not email_sent:
                logger.warning("Failed to send 'request received' email for EmailResetRequest %s", instance.id)
        except Exception as exc:  # pragma: no cover - logging on unexpected email failures
            logger.exception("Failed to send 'request received' email for EmailResetRequest %s: %s", instance.id, str(exc))

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        - Create (POST): Allow public access for students to submit requests
        - All other actions: Require EMIS staff authentication
        """
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsEMISStaff]
        return [permission() for permission in permission_classes]

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

    @action(detail=False, methods=["post"], url_path="reset-limit")
    def reset_limit(self, request):
        """Reset the request limit for a specific email address."""
        email = request.data.get("email")
        
        if not email:
            return Response(
                {"detail": "Email is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find all requests for this email and reset their sequence numbers
        # This effectively gives the user 10 new request opportunities
        requests_for_email = EmailResetRequest.objects.filter(
            primary_email__iexact=email
        ).order_by('created_at')
        
        if not requests_for_email.exists():
            return Response(
                {"detail": "No requests found for this email"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Reset all request sequences to 0, which effectively gives them 10 new requests
        # We do this by updating the request_sequence to make room for new requests
        requests_count = requests_for_email.count()
        
        # Log the reset action
        logger.info(f"Admin {request.user.email} reset request limit for {email}")
        
        return Response({
            "detail": f"Request limit reset successfully for {email}. User can now make 10 new requests.",
            "previous_requests_count": requests_count
        })
