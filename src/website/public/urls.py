from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Project Imports
from src.website.public.views import (
    PublicCampusAcademicCalenderListAPIView,
    PublicCampusDownloadListAPIView,
    PublicCampusEventViewSet,
    PublicCampusFeedbackCreateAPIView,
    PublicCampusInfoRetrieveAPIView,
    PublicCampusKeyOfficialListAPIView,
    PublicCampusReportListAPIView,
    PublicCampusSectionReadOnlyViewSet,
    PublicCampusUnitReadOnlyViewSet,
    PublicCampusUnionReadOnlyViewSet,
    PublicStudentClubEventViewSet,
    PublicStudentClubReadOnlyViewSet,
    PublicGlobalGalleryListAPIView,
)

router = DefaultRouter(trailing_slash=False)

router.register(
    "unions",
    PublicCampusUnionReadOnlyViewSet,
    basename="public-campus-union",
)
router.register(
    "clubs",
    PublicStudentClubReadOnlyViewSet,
    basename="public-campus-club",
)
router.register(
    "club-events",
    PublicStudentClubEventViewSet,
    basename="public-club-event",
)
router.register(
    "campus-events",
    PublicCampusEventViewSet,
    basename="public-campus-event",
)
router.register(
    "campus-sections",
    PublicCampusSectionReadOnlyViewSet,
    basename="public-campus-section",
)
router.register(
    "campus-units",
    PublicCampusUnitReadOnlyViewSet,
    basename="public-campus-unit",
)


urlpatterns = [
    path(
        "campus-info",
        PublicCampusInfoRetrieveAPIView.as_view(),
        name="public-campus-info",
    ),
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
    path("campus-key-officials", PublicCampusKeyOfficialListAPIView.as_view()),
    path(
        "submit-feedback",
        PublicCampusFeedbackCreateAPIView.as_view(),
        name="public-submit-feedback",
    ),
    path(
        "global-gallery",
        PublicGlobalGalleryListAPIView.as_view(),
        name="public-global-gallery",
    ),
    path("", include(router.urls)),
]
