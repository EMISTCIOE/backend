from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CampusInfoViewSet

router = DefaultRouter()
router.register("campus-info", CampusInfoViewSet, basename="campus-info")
urlpatterns = [
    path("", include(router.urls)),
]
