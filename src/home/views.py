from django.db.models import Q
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

from .models import (
    Calendar,
    HomePage,
    Image,
    ImageGallery,
    Report,
    Resource,
    SocialMedia,
    Unit,
)

from .serializer import (
    CalendarSerializer,
    HomePageSerializer,
    ImageGallerySerializer,
    ImageSerializer,
    ReportSerializer,
    ResourceSerializer,
    SocialMediaSerializer,
    UnitSerializer,
)

# Custom pagination class
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# Admin ViewSets (Full CRUD for authenticated users)
class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

class CalendarViewSet(viewsets.ModelViewSet):
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

class HomeViewSet(viewsets.ModelViewSet):
    queryset = HomePage.objects.all()
    serializer_class = HomePageSerializer
    permission_classes = [IsAuthenticated]

class SocialMediaViewSet(viewsets.ModelViewSet):
    queryset = SocialMedia.objects.all()
    serializer_class = SocialMediaSerializer
    permission_classes = [IsAuthenticated]

class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    @action(detail=False, methods=['get'])
    def archived(self, request):
        """Get archived resources for admin"""
        archived_resources = Resource.objects.filter(is_archived=True)
        serializer = self.get_serializer(archived_resources, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured resources for admin"""
        featured_resources = Resource.objects.filter(is_featured=True)
        serializer = self.get_serializer(featured_resources, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_featured(self, request, pk=None):
        """Toggle featured status of a resource"""
        resource = self.get_object()
        resource.is_featured = not resource.is_featured
        resource.save()
        return Response({
            'message': f'Resource {"featured" if resource.is_featured else "unfeatured"} successfully',
            'is_featured': resource.is_featured
        })

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

class ImageGalleryViewSet(viewsets.ModelViewSet):
    queryset = ImageGallery.objects.all()
    serializer_class = ImageGallerySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

# Admin Search Views
class ResourceSearchView(ListAPIView):
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        keyword = self.request.GET.get("keyword", "")
        title = self.request.GET.get("title", "")

        queryset = Resource.objects.filter(is_active=True)
        
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) | Q(description__icontains=keyword)
            )
            
        if title:
            queryset = queryset.filter(title__iexact=title)
        
        return queryset

class ImageSearchView(ListAPIView):
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        gallery_name = self.request.GET.get("gallery_name", "")
        image_name = self.request.GET.get("image_name", "")
        image_uuid = self.request.GET.get("image_uuid", "")
        
        queryset = Image.objects.filter(is_active=True)
        
        if gallery_name:
            queryset = queryset.filter(gallery__name__icontains=gallery_name)
        if image_name:
            queryset = queryset.filter(name__icontains=image_name)
        if image_uuid:
            queryset = queryset.filter(uuid__iexact=image_uuid)
            
        return queryset