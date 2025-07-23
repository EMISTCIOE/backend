from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CampusInfoAPIView, CampusKeyOfficialViewSet

router = DefaultRouter()

router.register(
    "campus-key-officials",
    CampusKeyOfficialViewSet,
    basename="campus-key-official",
)

urlpatterns = [
    path("campus-info", CampusInfoAPIView.as_view(), name="campus-info"),
    path("", include(router.urls)),
]
