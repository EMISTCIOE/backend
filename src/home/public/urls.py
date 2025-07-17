from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HomePagePublicViewSet, SocialMediaPublicViewSet,
    UnitPublicViewSet, ResourcePublicViewSet,
    ImageGalleryPublicViewSet, ImagePublicViewSet,
    CalendarPublicViewSet, ReportPublicViewSet
)

router = DefaultRouter()
router.register(r'homepage', HomePagePublicViewSet)
router.register(r'social-media', SocialMediaPublicViewSet)
router.register(r'units', UnitPublicViewSet)
router.register(r'resources', ResourcePublicViewSet)
router.register(r'galleries', ImageGalleryPublicViewSet)
router.register(r'images', ImagePublicViewSet)
router.register(r'calendars', CalendarPublicViewSet)
router.register(r'reports', ReportPublicViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
