from django.urls import path, include
from rest_framework import routers
from .viewsets import (
    HomeViewSet,
    SocialMediaViewSet,
    ResourceViewSet,
    UnitViewSet,
    ImageGalleryViewset,
    ImageViewset,
    ReportViewset,
    CalendarViewset,
)
from .views import ResourceSearchView

router = routers.DefaultRouter()
router.register(r"home", HomeViewSet)
router.register(r"socialmedias", SocialMediaViewSet)
router.register(r"resources", ResourceViewSet)
router.register(r"units", UnitViewSet)
router.register(r"images", ImageViewset)
router.register(r"gallery", ImageGalleryViewset)
router.register(r"report", ReportViewset)
router.register(r"calendar", CalendarViewset)

urlpatterns = [
    path("", include(router.urls)),
    path("resource-search/", ResourceSearchView.as_view(), name="resource-search"),
]
