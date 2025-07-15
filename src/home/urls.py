from django.urls import include, path
from rest_framework import routers

from .views import ImageSearchView, ResourceSearchView
from .viewsets import (
    CalendarViewset,
    HomeViewSet,
    ImageGalleryViewset,
    ImageViewset,
    ReportViewset,
    ResourceViewSet,
    SocialMediaViewSet,
    UnitViewSet,
)

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
    path("image-search/", ImageSearchView.as_view(), name="image-search"),
]
