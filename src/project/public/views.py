from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..models import Project, ProjectTag
from ..serializers import (
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectTagSerializer,
)


class PublicProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public API for projects (read-only)
    """

    permission_classes = [AllowAny]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "project_type",
        "department",
        "department__slug",
        "academic_program",
        "academic_program__slug",
        "is_featured",
    ]
    search_fields = ["title", "abstract", "technologies_used"]
    ordering_fields = ["created_at", "views_count", "title"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = (
            Project.objects.select_related("department", "academic_program")
            .prefetch_related("members__department", "tag_assignments__tag")
            .filter(is_published=True)
        )

        department_slug = self.request.query_params.get("department_slug")
        if department_slug:
            qs = qs.filter(department__slug=department_slug)

        program_slug = self.request.query_params.get("program_slug")
        if program_slug:
            qs = qs.filter(academic_program__slug=program_slug)

        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectListSerializer
        return ProjectDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to increment views"""
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=["views_count"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def featured(self, request):
        """Get featured projects"""
        featured_projects = self.get_queryset().filter(is_featured=True)[:6]
        serializer = ProjectListSerializer(featured_projects, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_department(self, request):
        """Get projects by department"""
        department_slug = request.query_params.get("department_slug")
        if department_slug:
            projects = self.get_queryset().filter(department__slug=department_slug)
            serializer = ProjectListSerializer(projects, many=True)
            return Response(serializer.data)
        return Response({"error": "department_slug parameter is required"}, status=400)

    @action(detail=False, methods=["get"])
    def by_program(self, request):
        """Get projects by academic program"""
        program_slug = request.query_params.get("program_slug")
        if program_slug:
            projects = self.get_queryset().filter(
                academic_program__slug=program_slug
            )
            serializer = ProjectListSerializer(projects, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "program_slug parameter is required"},
            status=400,
        )

    @action(detail=False, methods=["get"])
    def by_type(self, request):
        """Get projects by type"""
        project_type = request.query_params.get("type")
        if project_type:
            projects = self.get_queryset().filter(project_type=project_type)
            serializer = ProjectListSerializer(projects, many=True)
            return Response(serializer.data)
        return Response({"error": "type parameter is required"}, status=400)


class PublicProjectTagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public API for project tags (read-only)
    """

    queryset = ProjectTag.objects.all()
    serializer_class = ProjectTagSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering = ["name"]
