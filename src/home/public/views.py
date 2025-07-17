from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from src.home.models import (
    HomePage,
    SocialMedia,
    Unit,
    Resource,
    ImageGallery,
    Image,
    Calendar,
    Report,
)
from .serializer import (
    HomePagePublicSerializer,
    SocialMediaPublicSerializer,
    UnitPublicSerializer,
    ResourcePublicSerializer,
    ImageGalleryPublicSerializer,
    ImagePublicSerializer,
    CalendarPublicSerializer,
    ReportPublicSerializer,
)

class HomePagePublicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HomePage.objects.filter(is_active=True)
    serializer_class = HomePagePublicSerializer
    permission_classes = [AllowAny]

class SocialMediaPublicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SocialMedia.objects.filter(is_active=True)
    serializer_class = SocialMediaPublicSerializer
    permission_classes = [AllowAny]

class UnitPublicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Unit.objects.filter(is_active=True)
    serializer_class = UnitPublicSerializer
    permission_classes = [AllowAny]

class ResourcePublicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Resource.objects.filter(is_active=True)
    serializer_class = ResourcePublicSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_resources = Resource.objects.filter(is_active=True, is_featured=True)
        serializer = self.get_serializer(featured_resources, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        keyword = request.query_params.get('keyword', '')
        title = request.query_params.get('title', '')
        
        queryset = Resource.objects.filter(is_active=True)
        
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) | Q(description__icontains=keyword)
            )
        if title:
            queryset = queryset.filter(title__iexact=title)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ImageGalleryPublicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ImageGallery.objects.filter(is_active=True)
    serializer_class = ImageGalleryPublicSerializer
    permission_classes = [AllowAny]

class ImagePublicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Image.objects.filter(is_active=True)
    serializer_class = ImagePublicSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        gallery_name = request.query_params.get('gallery_name', '')
        image_name = request.query_params.get('image_name', '')
        
        queryset = Image.objects.filter(is_active=True)
        
        if gallery_name:
            queryset = queryset.filter(gallery__name__icontains=gallery_name)
        if image_name:
            queryset = queryset.filter(name__icontains=image_name)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class CalendarPublicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Calendar.objects.filter(is_active=True)
    serializer_class = CalendarPublicSerializer
    permission_classes = [AllowAny]

class ReportPublicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Report.objects.filter(is_active=True)
    serializer_class = ReportPublicSerializer
    permission_classes = [AllowAny]
