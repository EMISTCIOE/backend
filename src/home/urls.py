from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HomeViewSet, SocialMediaViewSet, UnitViewSet,
    ResourceViewSet, ImageGalleryViewSet, ImageViewSet,
    CalendarViewSet, ReportViewSet,
    ResourceSearchView, ImageSearchView
)

router = DefaultRouter()
router.register(r'homepage', HomeViewSet)
router.register(r'social-media', SocialMediaViewSet)
router.register(r'units', UnitViewSet)
router.register(r'resources', ResourceViewSet)
router.register(r'galleries', ImageGalleryViewSet)
router.register(r'images', ImageViewSet)
router.register(r'calendars', CalendarViewSet)
router.register(r'reports', ReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('resource-search/', ResourceSearchView.as_view(), name='resource-search'),
    path('image-search/', ImageSearchView.as_view(), name='image-search'),
]
