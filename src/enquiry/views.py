"""
Enquiry Views
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from src.libs.pagination import CustomPagination
from src.user.models import User

from .models import MeetingEnquiry
from .serializers import (
    AdminListSerializer,
    MeetingEnquiryCreateSerializer,
    MeetingEnquiryDetailSerializer,
    MeetingEnquiryListSerializer,
    MeetingEnquiryResponseSerializer,
)


class MeetingEnquiryViewSet(viewsets.ModelViewSet):
    """
    Meeting Enquiry ViewSet
    - Public can create enquiries
    - Only requested admin can view/respond to their enquiries
    - EMIS/Campus Admins can view all
    """

    queryset = MeetingEnquiry.objects.all().select_related(
        "requested_admin",
        "responded_by",
    )
    pagination_class = CustomPagination

    def get_permissions(self):
        """Public can create, authenticated users can view their own"""
        if self.action == "create" or self.action == "available_admins":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return MeetingEnquiryCreateSerializer
        elif self.action == "respond":
            return MeetingEnquiryResponseSerializer
        elif self.action == "retrieve":
            return MeetingEnquiryDetailSerializer
        elif self.action == "available_admins":
            return AdminListSerializer
        return MeetingEnquiryListSerializer

    def get_queryset(self):
        """Filter based on user role"""
        user = self.request.user

        if not user.is_authenticated:
            return MeetingEnquiry.objects.none()

        # EMIS Staff and Campus Admins can see all
        if user.is_emis_staff() or user.is_campus_admin():
            queryset = self.queryset
        # Requested admin can see their own
        else:
            queryset = self.queryset.filter(requested_admin=user)

        # Filter by status
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by("-created_at")

    def create(self, request, *args, **kwargs):
        """Public endpoint to create enquiry"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """List enquiries based on permissions"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="respond")
    def respond(self, request, pk=None):
        """Admin responds to meeting enquiry"""
        enquiry = self.get_object()

        # Check if user can respond
        if not (
            request.user.is_emis_staff()
            or request.user.is_campus_admin()
            or enquiry.requested_admin == request.user
        ):
            return Response(
                {"error": "You don't have permission to respond to this enquiry."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(enquiry, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="available-admins")
    def available_admins(self, request):
        """Public endpoint to get list of available admins"""
        allowed_roles = {
            User.RoleType.ADMIN,
            User.RoleType.DEPARTMENT_ADMIN,
            User.RoleType.EMIS_STAFF,
        }
        admins = User.objects.filter(
            is_active=True,
            is_archived=False,
            role__in=allowed_roles,
        ).order_by("first_name")

        serializer = self.get_serializer(admins, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="my-requests")
    def my_requests(self, request):
        """Get enquiries for the logged-in admin"""
        queryset = self.queryset.filter(requested_admin=request.user)
        
        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
