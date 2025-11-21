from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .listing_apis.views import FiscalSessionBSForCampusReportListAPIView
from .views import (
    AcademicCalendarViewSet,
    CampusDownloadViewSet,
    CampusFeedbackViewSet,
    CampusInfoAPIView,
    CampusKeyOfficialViewSet,
    CampusReportViewSet,
    CampusSectionViewSet,
    CampusStaffDesignationViewSet,
    CampusUnionViewSet,
    CampusUnitViewSet,
    ResearchFacilityViewSet,
    GlobalEventViewSet,
    GlobalGalleryImageViewSet,
    GlobalGalleryListAPIView,
    SocialMediaLinkDeleteAPIView,
    StudentClubViewSet,
)

router = DefaultRouter(trailing_slash=False)

router.register(
    "campus-key-officials",
    CampusKeyOfficialViewSet,
    basename="campus-key-official",
)
router.register(
    "campus-staff-designations",
    CampusStaffDesignationViewSet,
    basename="campus-staff-designation",
)
router.register("campus-feedbacks", CampusFeedbackViewSet, basename="campus-feedback")
router.register("campus-downloads", CampusDownloadViewSet, basename="campus-download")
router.register("campus-reports", CampusReportViewSet, basename="campus-report")
router.register(
    "academic-calendars",
    AcademicCalendarViewSet,
    basename="academic-calendar",
)
router.register("student-clubs", StudentClubViewSet, basename="student-club")
router.register("campus-unions", CampusUnionViewSet, basename="campus-unions")
router.register("campus-sections", CampusSectionViewSet, basename="campus-section")
router.register("campus-units", CampusUnitViewSet, basename="campus-unit")
router.register("research-facilities", ResearchFacilityViewSet, basename="research-facility")
router.register(
    "gallery-images",
    GlobalGalleryImageViewSet,
    basename="gallery-image",
)
router.register(
    "global-events",
    GlobalEventViewSet,
    basename="global-event",
)

urlpatterns = [
    path("campus-info", CampusInfoAPIView.as_view(), name="campus-info"),
    path(
        "campus-info/social-media-links/<int:pk>/delete",
        SocialMediaLinkDeleteAPIView.as_view(),
    ),
    # Listing APIs
    path(
        "campus-reports/fiscal-sessions",
        FiscalSessionBSForCampusReportListAPIView.as_view(),
    ),
    path("global-gallery", GlobalGalleryListAPIView.as_view(), name="global-gallery"),
    path("", include(router.urls)),
]
