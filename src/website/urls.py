from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CampusInfoAPIView,
    CampusKeyOfficialViewSet,
    SocialMediaLinkDeleteAPIView,
    CampusEventViewSet,
    CampusReportViewSet,
)

router = DefaultRouter()

router.register(
    "campus-key-officials",
    CampusKeyOfficialViewSet,
    basename="campus-key-official",
)

router.register("campus-reports", CampusReportViewSet, basename="campus-report")
router.register("campus-events", CampusEventViewSet, basename="campus-event")

urlpatterns = [
    path("campus-info", CampusInfoAPIView.as_view(), name="campus-info"),
    path(
        "campus-info/social-media-links/<int:pk>/delete",
        SocialMediaLinkDeleteAPIView.as_view(),
    ),
    path("", include(router.urls)),
]
