from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Research, ResearchCategory
from ..serializers import ResearchListSerializer, ResearchDetailSerializer, ResearchCategorySerializer


class PublicResearchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public API for research (read-only)
    """
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['research_type', 'department', 'is_featured', 'status']
    search_fields = ['title', 'abstract', 'keywords']
    ordering_fields = ['created_at', 'views_count', 'title', 'start_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Research.objects.select_related('department').prefetch_related(
            'participants__department', 'category_assignments__category', 'publications'
        ).filter(is_published=True)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ResearchListSerializer
        return ResearchDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to increment views"""
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured research"""
        featured_research = self.get_queryset().filter(is_featured=True)[:6]
        serializer = ResearchListSerializer(featured_research, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get research by department"""
        department_slug = request.query_params.get('department_slug')
        if department_slug:
            research = self.get_queryset().filter(department__slug=department_slug)
            serializer = ResearchListSerializer(research, many=True)
            return Response(serializer.data)
        return Response({"error": "department_slug parameter is required"}, status=400)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get research by type"""
        research_type = request.query_params.get('type')
        if research_type:
            research = self.get_queryset().filter(research_type=research_type)
            serializer = ResearchListSerializer(research, many=True)
            return Response(serializer.data)
        return Response({"error": "type parameter is required"}, status=400)
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get research by status"""
        status_filter = request.query_params.get('status')
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
    search_fields = ['name', 'description']
    ordering = ['name']