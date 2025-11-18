from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Research, ResearchCategory
from .serializers import (
    ResearchCategorySerializer,
    ResearchCreateUpdateSerializer,
    ResearchDetailSerializer,
    ResearchListSerializer,
)


class ResearchViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing research
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "status",
        "research_type",
        "department",
        "is_featured",
        "is_published",
    ]
    search_fields = [
        "title",
        "description",
        "abstract",
        "principal_investigator",
        "keywords",
    ]
    ordering_fields = ["created_at", "updated_at", "title", "views_count", "start_date"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            Research.objects.select_related("department")
            .prefetch_related(
                "participants__department",
                "category_assignments__category",
                "publications",
            )
            .all()
        )

    def get_serializer_class(self):
        if self.action == "list":
            return ResearchListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return ResearchCreateUpdateSerializer
        return ResearchDetailSerializer

    @action(detail=True, methods=["post"])
    def increment_views(self, request, pk=None):
        """Increment the views count for a research"""
        research = self.get_object()
        research.views_count += 1
        research.save(update_fields=["views_count"])
        return Response({"views_count": research.views_count})

    @action(detail=False, methods=["get"])
    def featured(self, request):
        """Get featured research"""
        featured_research = self.get_queryset().filter(
            is_featured=True,
            is_published=True,
        )
        serializer = ResearchListSerializer(featured_research, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_department(self, request):
        """Get research grouped by department"""
        department_id = request.query_params.get("department_id")
        if department_id:
            research = self.get_queryset().filter(
                department_id=department_id,
                is_published=True,
            )
            serializer = ResearchListSerializer(research, many=True)
            return Response(serializer.data)
        return Response({"error": "department_id parameter is required"}, status=400)

    @action(detail=False, methods=["get"])
    def by_participant(self, request):
        """Get research by participant"""
        participant_name = request.query_params.get("participant_name")
        participant_type = request.query_params.get("participant_type")

        queryset = self.get_queryset()

        if participant_name:
            queryset = queryset.filter(
                participants__full_name__icontains=participant_name,
            )

        if participant_type:
            queryset = queryset.filter(participants__participant_type=participant_type)

        queryset = queryset.distinct()
        serializer = ResearchListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_funding(self, request):
        """Get research by funding agency"""
        funding_agency = request.query_params.get("funding_agency")
        if funding_agency:
            research = self.get_queryset().filter(
                funding_agency__icontains=funding_agency,
                is_published=True,
            )
            serializer = ResearchListSerializer(research, many=True)
            return Response(serializer.data)
        return Response({"error": "funding_agency parameter is required"}, status=400)

    @action(detail=False, methods=["get"])
    def search_advanced(self, request):
        """Advanced search with multiple filters"""
        queryset = self.get_queryset()

        # Filter by keyword
        keyword = request.query_params.get("keyword")
        if keyword:
            queryset = queryset.filter(keywords__icontains=keyword)

        # Filter by funding range
        min_funding = request.query_params.get("min_funding")
        max_funding = request.query_params.get("max_funding")
        if min_funding:
            queryset = queryset.filter(funding_amount__gte=min_funding)
        if max_funding:
            queryset = queryset.filter(funding_amount__lte=max_funding)

        # Filter by date range
        start_year = request.query_params.get("start_year")
        end_year = request.query_params.get("end_year")
        if start_year:
            queryset = queryset.filter(start_date__year__gte=start_year)
        if end_year:
            queryset = queryset.filter(end_date__year__lte=end_year)

        # Filter by category
        category_id = request.query_params.get("category_id")
        if category_id:
            queryset = queryset.filter(category_assignments__category_id=category_id)

        queryset = queryset.distinct()
        serializer = ResearchListSerializer(queryset, many=True)
        return Response(serializer.data)


class ResearchCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing research categories
    """

    queryset = ResearchCategory.objects.all()
    serializer_class = ResearchCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]
