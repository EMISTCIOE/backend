from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Project Imports
from src.website.public.views import (
    PublicCampusInfoRetrieveAPIView,
    PublicCampusDownloadListAPIView,
    PublicCampusEventListAPIView,
    PublicCampusEventRetrieveAPIView,
    PublicCampusKeyOfficialListAPIView,
)

router = DefaultRouter()

urlpatterns = [
    path("campus-info", PublicCampusInfoRetrieveAPIView.as_view(), name="campus-info"),
    path(
        "campus-downloads",
        PublicCampusDownloadListAPIView.as_view(),
        name="public-campus-downloads",
    ),
    path(
        "campus-events",
        PublicCampusEventListAPIView.as_view(),
        name="public-campus-event-list",
    ),
    path(
        "campus-events/<uuid:uuid>",
        PublicCampusEventRetrieveAPIView.as_view(),
        name="public-campus-event-detail",
    ),
    path("campus-key-officials", PublicCampusKeyOfficialListAPIView.as_view()),
    path("", include(router.urls)),
]
