from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Project Imports
from src.website.public.views import (
    PublicCampusDownloadListAPIView,
    PublicCampusEventListAPIView,
    PublicCampusEventRetrieveAPIView,
    PublicCampusFeedbackCreateAPIView,
    PublicCampusInfoRetrieveAPIView,
    PublicCampusKeyOfficialListAPIView,
    PublicCampusReportListAPIView,
    PublicCampusAcademicCalenderListAPIView,
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
        "campus-reports",
        PublicCampusReportListAPIView.as_view(),
        name="public-campus-reports",
    ),
    path(
        "academic-calendars",
        PublicCampusAcademicCalenderListAPIView.as_view(),
        name="public-campus-academic-calenders",
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
    path(
        "submit-feedback",
        PublicCampusFeedbackCreateAPIView.as_view(),
        name="submit-feedback",
    ),
    path("", include(router.urls)),
]
