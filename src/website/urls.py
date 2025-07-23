from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CampusInfoViewSet,CampusKeyOfficialViewSet

router = DefaultRouter()
router.register("campus-info", CampusInfoViewSet, basename="campus-info")
router.register("campus-key-officials", CampusKeyOfficialViewSet, basename="campus-key-official")
urlpatterns = [
    path("", include(router.urls)),
]
