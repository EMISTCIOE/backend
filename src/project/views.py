from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Project, ProjectTag
from .serializers import (
    ProjectCreateUpdateSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectTagSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing projects
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "status",
        "project_type",
        "department",
        "academic_program",
        "is_featured",
        "is_published",
    ]
    search_fields = [
        "title",
        "description",
        "abstract",
        "supervisor_name",
        "technologies_used",
    ]
    ordering_fields = ["created_at", "updated_at", "title", "views_count"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            Project.objects.select_related("department", "academic_program")
            .prefetch_related("members__department", "tag_assignments__tag")
            .all()
        )

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return ProjectCreateUpdateSerializer
        return ProjectDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=["post"])
    def increment_views(self, request, pk=None):
        """Increment the views count for a project"""
        project = self.get_object()
        project.views_count += 1
        project.save(update_fields=["views_count"])
        return Response({"views_count": project.views_count})

    @action(detail=False, methods=["get"])
    def featured(self, request):
        """Get featured projects"""
        featured_projects = self.get_queryset().filter(
            is_featured=True,
            is_published=True,
        )
        serializer = ProjectListSerializer(featured_projects, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_department(self, request):
        """Get projects grouped by department"""
        department_id = request.query_params.get("department_id")
        if department_id:
            projects = self.get_queryset().filter(
                department_id=department_id,
                is_published=True,
            )
            serializer = ProjectListSerializer(projects, many=True)
            return Response(serializer.data)
        return Response({"error": "department_id parameter is required"}, status=400)

    @action(detail=False, methods=["get"])
    def by_program(self, request):
        """Get projects grouped by academic program"""
        program_id = request.query_params.get("program_id")
        if program_id:
            projects = self.get_queryset().filter(
                academic_program_id=program_id,
                is_published=True,
            )
            serializer = ProjectListSerializer(projects, many=True)
            return Response(serializer.data)
        return Response({"error": "program_id parameter is required"}, status=400)

    @action(detail=False, methods=["get"])
    def search_advanced(self, request):
        """Advanced search with multiple filters"""
        queryset = self.get_queryset()

        # Filter by academic year
        academic_year = request.query_params.get("academic_year")
        if academic_year:
            queryset = queryset.filter(academic_year__icontains=academic_year)

        # Filter by technology
        technology = request.query_params.get("technology")
        if technology:
            queryset = queryset.filter(technologies_used__icontains=technology)

        # Filter by member roll number
        roll_number = request.query_params.get("roll_number")
        if roll_number:
            queryset = queryset.filter(members__roll_number__icontains=roll_number)

        # Filter by tag
        tag_id = request.query_params.get("tag_id")
        if tag_id:
            queryset = queryset.filter(tag_assignments__tag_id=tag_id)

        queryset = queryset.distinct()
        serializer = ProjectListSerializer(queryset, many=True)
        return Response(serializer.data)


class ProjectTagViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing project tags
    """

    queryset = ProjectTag.objects.all()
    serializer_class = ProjectTagSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
