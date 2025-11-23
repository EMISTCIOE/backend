from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..models import Research, ResearchCategory
from ..serializers import (
    ResearchCategorySerializer,
    ResearchDetailSerializer,
    ResearchListSerializer,
)


class PublicResearchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public API for research (read-only)
    """

    permission_classes = [AllowAny]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "research_type",
        "department",
        "department__slug",
        "academic_program",
        "academic_program__slug",
        "is_featured",
        "status",
        "slug",
    ]
    search_fields = ["title", "abstract", "keywords"]
    ordering_fields = ["created_at", "views_count", "title", "start_date"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = (
            Research.objects.select_related("department", "academic_program")
            .prefetch_related(
                "participants__department",
                "category_assignments__category",
                "publications",
            )
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
            return ResearchListSerializer
        return ResearchDetailSerializer

    def get_object(self):
        """Allow lookup by slug or ID for public research detail."""
        queryset = self.filter_queryset(self.get_queryset())
        lookup_value = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field)

        if lookup_value is None:
            raise Http404("Research not specified")

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
        """Get featured research"""
        featured_research = self.get_queryset().filter(is_featured=True)[:6]
        serializer = ResearchListSerializer(featured_research, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_department(self, request):
        """Get research by department"""
        department_slug = request.query_params.get("department_slug")
        if department_slug:
            research = self.get_queryset().filter(department__slug=department_slug)
            serializer = ResearchListSerializer(research, many=True)
            return Response(serializer.data)
        return Response({"error": "department_slug parameter is required"}, status=400)

    @action(detail=False, methods=["get"])
    def by_program(self, request):
        """Get research by academic program"""
        program_slug = request.query_params.get("program_slug")
        if program_slug:
            research = self.get_queryset().filter(
                academic_program__slug=program_slug
            )
            serializer = ResearchListSerializer(research, many=True)
            return Response(serializer.data)
        return Response(
            {"error": "program_slug parameter is required"},
            status=400,
        )

    @action(detail=False, methods=["get"])
    def by_type(self, request):
        """Get research by type"""
        research_type = request.query_params.get("type")
        if research_type:
            research = self.get_queryset().filter(research_type=research_type)
            serializer = ResearchListSerializer(research, many=True)
            return Response(serializer.data)
        return Response({"error": "type parameter is required"}, status=400)

    @action(detail=False, methods=["get"])
    def by_status(self, request):
        """Get research by status"""
        status_filter = request.query_params.get("status")
        if status_filter:
            research = self.get_queryset().filter(status=status_filter)
            serializer = ResearchListSerializer(research, many=True)
            return Response(serializer.data)
        return Response({"error": "status parameter is required"}, status=400)


class PublicResearchCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public API for research categories (read-only)
    """

    queryset = ResearchCategory.objects.all()
    serializer_class = ResearchCategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering = ["name"]
