from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Project Imports
from src.website.public.views import (
    PublicCampusInfoRetrieveAPIView,
    PublicCampusDownloadListAPIView,
)

router = DefaultRouter()

urlpatterns = [
    path("campus-info", PublicCampusInfoRetrieveAPIView.as_view(), name="campus-info"),
    path(
        "campus-downloads",
        PublicCampusDownloadListAPIView.as_view(),
        name="public-campus-downloads",
    ),
    path("", include(router.urls)),
]
