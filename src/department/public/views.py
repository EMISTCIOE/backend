from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.shortcuts import get_object_or_404

# Project Imports
from src.department.models import (
    Department,
    DepartmentEventGallery,
)

from src.department.public.serializer import (
    PublicDepartmentListSerializer,
    PublicDepartmentDetailSerializer,
    PublicDepartmentStaffSerializer,
    PublicDepartmentProgramSerializer,
    PublicDepartmentDownloadSerializer,
    PublicDepartmentPlanSerializer,
    PublicDepartmentEventSerializer,
    PublicDepartmentEventGallerySerializer,
)


class PublicDepartmentListAPIView(ListAPIView):
    """Public API to list all departments"""

    permission_classes = [AllowAny]
    serializer_class = PublicDepartmentListSerializer
    queryset = Department.objects.filter(is_active=True)
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ["name", "short_name"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]


class PublicDepartmentRetrieveAPIView(RetrieveAPIView):
    """Public API to retrieve single department by slug"""

    permission_classes = [AllowAny]
    serializer_class = PublicDepartmentDetailSerializer
    lookup_field = "slug"
    queryset = Department.objects.filter(is_active=True)


class PublicDepartmentStaffListAPIView(ListAPIView):
    """List staff members in a department"""

    permission_classes = [AllowAny]
    serializer_class = PublicDepartmentStaffSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "designation"]
    ordering_fields = ["display_order", "name"]
    ordering = ["display_order"]

    def get_queryset(self):
        department = get_object_or_404(
            Department, slug=self.kwargs["slug"], is_active=True
        )
        return department.department_staffs.filter(is_active=True)


class PublicDepartmentProgramListAPIView(ListAPIView):
    """List academic programs in a department"""

    permission_classes = [AllowAny]
    serializer_class = PublicDepartmentProgramSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "short_name"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        department = get_object_or_404(
            Department, slug=self.kwargs["slug"], is_active=True
        )
        return department.department_programs.filter(is_active=True)


class PublicDepartmentDownloadListAPIView(ListAPIView):
    """List department downloads"""

    permission_classes = [AllowAny]
    serializer_class = PublicDepartmentDownloadSerializer
    ordering = ["-created_at"]

    def get_queryset(self):
        department = get_object_or_404(
            Department, slug=self.kwargs["slug"], is_active=True
        )
        return department.downloads.filter(is_active=True)


class PublicDepartmentEventListAPIView(ListAPIView):
    """List department events"""

    permission_classes = [AllowAny]
    serializer_class = PublicDepartmentEventSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ["title"]
    ordering_fields = ["event_start_date", "created_at"]
    ordering = ["-event_start_date"]
    filterset_fields = ["event_type"]

    def get_queryset(self):
        department = get_object_or_404(
            Department, slug=self.kwargs["slug"], is_active=True
        )
        return department.events.filter(is_active=True)


class PublicDepartmentEventGalleryListAPIView(ListAPIView):
    """List gallery images for an event"""

    permission_classes = [AllowAny]
    serializer_class = PublicDepartmentEventGallerySerializer

    def get_queryset(self):
        return DepartmentEventGallery.objects.filter(
            uuid=self.kwargs["event_id"], is_active=True
        )


class PublicDepartmentPlanPolicyListAPIView(ListAPIView):
    """List plans and policies of a department"""

    permission_classes = [AllowAny]
    serializer_class = PublicDepartmentPlanSerializer
    ordering = ["-created_at"]

    def get_queryset(self):
        department = get_object_or_404(
            Department, slug=self.kwargs["slug"], is_active=True
        )
        return department.plans_and_policies.filter(is_active=True)
