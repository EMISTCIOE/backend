from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
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
        "status",
        "slug",
    ]
    search_fields = [
        "title",
        "abstract",
        "technologies_used",
        "supervisor_name",
        "members__full_name",
    ]
    ordering_fields = ["created_at", "views_count", "title", "start_date"]
    ordering = ["-created_at"]

    def _apply_limit_offset(self, queryset):
        """Apply limit/offset params for custom actions without using paginated responses."""
        try:
            limit = int(self.request.query_params.get("limit", 0))
        except (TypeError, ValueError):
            limit = 0
        try:
            offset = int(self.request.query_params.get("offset", 0))
        except (TypeError, ValueError):
            offset = 0

        if limit and limit > 0:
            return queryset[offset : offset + limit]
        if offset:
            return queryset[offset:]
        return queryset

    def get_queryset(self):
        qs = (
            Project.objects.select_related("department", "academic_program")
            .prefetch_related("members__department", "tag_assignments__tag")
            .filter(is_published=True)
        )

        # Support filtering via tag slugs or IDs (comma separated)
        tags_param = self.request.query_params.get("tags")
        if tags_param:
            tags = [tag.strip() for tag in tags_param.split(",") if tag.strip()]
            tag_ids = [int(tag) for tag in tags if tag.isdigit()]
            tag_slugs = [tag for tag in tags if not tag.isdigit()]
            tag_filter = Q()
            if tag_ids:
                tag_filter |= Q(tag_assignments__tag__id__in=tag_ids)
            if tag_slugs:
                tag_filter |= Q(tag_assignments__tag__slug__in=tag_slugs)
            if tag_filter:
                qs = qs.filter(tag_filter)

        department_slug = self.request.query_params.get("department_slug")
        if department_slug:
            qs = qs.filter(department__slug=department_slug)

        program_slug = self.request.query_params.get("program_slug")
        if program_slug:
            qs = qs.filter(academic_program__slug=program_slug)

        return qs.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectListSerializer
        return ProjectDetailSerializer

    def get_object(self):
        """Allow lookup by slug or ID for public project detail."""
        queryset = self.filter_queryset(self.get_queryset())
        lookup_value = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field)

        if lookup_value is None:
            raise Http404("Project not specified")

        obj = queryset.filter(slug=lookup_value).first()
        if obj is None:
            obj = get_object_or_404(queryset, pk=lookup_value)

        self.check_object_permissions(self.request, obj)
        return obj

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
        if not department_slug:
            return Response(
                {"error": "department_slug parameter is required"},
                status=400,
            )

        projects = self.filter_queryset(
            self.get_queryset().filter(department__slug=department_slug)
        )
        projects = self._apply_limit_offset(projects)
        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_program(self, request):
        """Get projects by academic program"""
        program_slug = request.query_params.get("program_slug")
        if not program_slug:
            return Response(
                {"error": "program_slug parameter is required"},
                status=400,
            )

        projects = self.filter_queryset(
            self.get_queryset().filter(academic_program__slug=program_slug)
        )
        projects = self._apply_limit_offset(projects)
        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_type(self, request):
        """Get projects by type"""
        project_type = request.query_params.get("type")
        if not project_type:
            return Response({"error": "type parameter is required"}, status=400)

        projects = self.filter_queryset(
            self.get_queryset().filter(project_type=project_type)
        )
        projects = self._apply_limit_offset(projects)
        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_status(self, request):
        """Get projects by status"""
        status_filter = request.query_params.get("status")
        if not status_filter:
            return Response({"error": "status parameter is required"}, status=400)

        projects = self.filter_queryset(
            self.get_queryset().filter(status=status_filter)
        )
        projects = self._apply_limit_offset(projects)
        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data)


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
