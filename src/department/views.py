# Django Imports
import django_filters
from django.db import transaction
from django_filters.filterset import FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.exceptions import NotFound

# Rest Framework Imports
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from src.libs.utils import set_binary_files_null_if_empty

# Project Imports
from .messages import (
    ACADEMIC_PROGRAM_DELETED_SUCCESS,
    ACADEMIC_PROGRAM_NOT_FOUND,
    DEPARTMENT_DOWNLOAD_DELETED_SUCCESS,
    DEPARTMENT_DOWNLOAD_NOT_FOUND,
    DEPARTMENT_PLANS_DELETED_SUCCESS,
    DEPARTMENT_PLANS_NOT_FOUND,
    SOCIAL_LINK_DELETED_SUCCESS,
    SOCIAL_LINK_NOT_FOUND,
)
from .models import (
    AcademicProgram,
    Department,
    DepartmentDownload,
    DepartmentPlanAndPolicy,
    DepartmentSocialMedia,
)
from .permissions import (
    AcademicProgramPermission,
    DepartmentDownloadPermission,
    DepartmentPermission,
    DepartmentPlanAndPolicyPermission,
)
from .serializers import (
    AcademicProgramCreateSerializer,
    AcademicProgramListSerializer,
    AcademicProgramPatchSerializer,
    AcademicProgramRetrieveSerializer,
    DepartmentCreateSerializer,
    DepartmentDownloadCreateSerializer,
    DepartmentDownloadListSerializer,
    DepartmentDownloadPatchSerializer,
    DepartmentDownloadRetrieveSerializer,
    DepartmentListSerializer,
    DepartmentPatchSerializer,
    DepartmentPlanAndPolicyCreateSerializer,
    DepartmentPlanAndPolicyListSerializer,
    DepartmentPlanAndPolicyPatchSerializer,
    DepartmentPlanAndPolicyRetrieveSerializer,
    DepartmentRetrieveSerializer,
)


class FilterForDepartmentViewSet(FilterSet):
    """Filters For Department ViewSet"""

    class Meta:
        model = Department
        fields = ["short_name", "is_active"]


class DepartmentViewSet(ModelViewSet):
    """
    ViewSet for managing CRUD operations for Department.
    """

    permission_classes = [DepartmentPermission]
    filterset_class = FilterForDepartmentViewSet
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["name", "short_name"]
    queryset = Department.objects.filter(is_archived=False)
    ordering_fields = ["-created_at", "short_name"]
    http_method_names = ["options", "head", "get", "patch", "post", "delete"]

    def get_serializer_class(self):
        serializer_class = None

        if self.request.method == "GET":
            if self.action == "list":
                serializer_class = DepartmentListSerializer
            else:
                serializer_class = DepartmentRetrieveSerializer

        if self.request.method == "POST":
            serializer_class = DepartmentCreateSerializer
        elif self.request.method == "PATCH":
            serializer_class = DepartmentPatchSerializer

        return serializer_class

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # set blank file fields to None/null
        file_fields = ["thumbnail"]
        if file_fields:
            set_binary_files_null_if_empty(file_fields, request.data)
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        # set blank file fields to None/null
        file_fields = ["thumbnail"]
        if file_fields:
            set_binary_files_null_if_empty(file_fields, request.data)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Delete a department along with its thumbnail file."""
        try:
            instance = self.get_object()
        except Exception:
            return Response(
                {"detail": "Department not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if instance.thumbnail:
            instance.thumbnail.delete(save=False)

        instance.delete()
        return Response(
            {"message": "Department deleted successfully"},
            status=status.HTTP_200_OK,
        )


class DepartmentSocialMediaDestroyAPIView(generics.DestroyAPIView):
    permission_classes = [DepartmentPermission]
    lookup_url_kwarg = "social_link_id"
    queryset = DepartmentSocialMedia.objects.all()

    def get_object(self):
        obj = self.queryset.filter(
            department_id=self.kwargs["department_id"],
            pk=self.kwargs[self.lookup_url_kwarg],
        ).first()
        if not obj:
            raise NotFound({"detail": SOCIAL_LINK_NOT_FOUND})
        return obj

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"message": SOCIAL_LINK_DELETED_SUCCESS},
            status=status.HTTP_200_OK,
        )


class FilterForAcademicProgramViewSet(FilterSet):
    class Meta:
        model = AcademicProgram
        fields = ["department", "program_type", "short_name", "is_active"]


class AcademicProgramViewSet(ModelViewSet):
    permission_classes = [AcademicProgramPermission]
    filterset_class = FilterForAcademicProgramViewSet
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["name", "short_name", "description"]
    queryset = AcademicProgram.objects.filter(is_archived=False)
    ordering_fields = ["-created_at", "name", "short_name"]
    http_method_names = ["options", "head", "get", "patch", "post", "delete"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return (
                AcademicProgramListSerializer
                if self.action == "list"
                else AcademicProgramRetrieveSerializer
            )
        if self.request.method == "POST":
            return AcademicProgramCreateSerializer
        if self.request.method == "PATCH":
            return AcademicProgramPatchSerializer
        return AcademicProgramRetrieveSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["thumbnail"], request.data)
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["thumbnail"], request.data)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.thumbnail.delete(save=False)
        except Exception:
            return Response(
                {"detail": ACADEMIC_PROGRAM_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        instance.delete()
        return Response(
            {"message": ACADEMIC_PROGRAM_DELETED_SUCCESS},
            status=status.HTTP_200_OK,
        )


class FilterForDepartmentDownloadViewSet(FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_at")

    class Meta:
        model = DepartmentDownload
        fields = ["department", "is_active", "date"]


class DepartmentDownloadViewSet(ModelViewSet):
    permission_classes = [DepartmentDownloadPermission]
    filterset_class = FilterForDepartmentDownloadViewSet
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["title", "description"]
    queryset = DepartmentDownload.objects.filter(is_archived=False)
    ordering_fields = ["-created_at", "title"]
    http_method_names = ["options", "head", "get", "patch", "post", "delete"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return (
                DepartmentDownloadListSerializer
                if self.action == "list"
                else DepartmentDownloadRetrieveSerializer
            )
        if self.request.method == "POST":
            return DepartmentDownloadCreateSerializer
        if self.request.method == "PATCH":
            return DepartmentDownloadPatchSerializer
        return DepartmentDownloadRetrieveSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["file"], request.data)
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["file"], request.data)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.file.delete(save=False)

        except Exception:
            return Response(
                {"detail": DEPARTMENT_DOWNLOAD_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        instance.delete()
        return Response(
            {"message": DEPARTMENT_DOWNLOAD_DELETED_SUCCESS},
            status=status.HTTP_200_OK,
        )


class FilterForDepartmentPlanAndPolicyViewSet(FilterSet):
    class Meta:
        model = DepartmentPlanAndPolicy
        fields = ["department", "is_active"]


class DepartmentPlanAndPolicyViewSet(ModelViewSet):
    permission_classes = [DepartmentPlanAndPolicyPermission]
    filterset_class = FilterForDepartmentPlanAndPolicyViewSet
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["title"]
    queryset = DepartmentPlanAndPolicy.objects.filter(is_archived=False)
    ordering_fields = ["-created_at", "title"]
    http_method_names = ["options", "head", "get", "patch", "post", "delete"]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return (
                DepartmentPlanAndPolicyListSerializer
                if self.action == "list"
                else DepartmentPlanAndPolicyRetrieveSerializer
            )
        if self.request.method == "POST":
            return DepartmentPlanAndPolicyCreateSerializer
        if self.request.method == "PATCH":
            return DepartmentPlanAndPolicyPatchSerializer
        return DepartmentPlanAndPolicyRetrieveSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["file"], request.data)
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        set_binary_files_null_if_empty(["file"], request.data)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.file.delete(save=False)
        except Exception:
            return Response(
                {"detail": DEPARTMENT_PLANS_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        instance.delete()
        return Response(
            {"message": DEPARTMENT_PLANS_DELETED_SUCCESS},
            status=status.HTTP_200_OK,
        )
