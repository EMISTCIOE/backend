from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .listing_apis.views import FiscalSessionBSForCampusReportListAPIView
from .views import (
    AcademicCalendarViewSet,
    CampusDownloadViewSet,
    CampusEventGalleryDestroyAPIView,
    CampusEventViewSet,
    CampusFeedbackViewSet,
    CampusInfoAPIView,
    CampusKeyOfficialViewSet,
    CampusReportViewSet,
    CampusUnionViewSet,
    SocialMediaLinkDeleteAPIView,
    StudentClubEventGalleryDestroyAPIView,
    StudentClubEventViewSet,
    StudentClubViewSet,
)

router = DefaultRouter(trailing_slash=False)

router.register(
    "campus-key-officials",
    CampusKeyOfficialViewSet,
    basename="campus-key-official",
)
router.register("campus-feedbacks", CampusFeedbackViewSet, basename="campus-feedback")
router.register("campus-downloads", CampusDownloadViewSet, basename="campus-download")
router.register("campus-reports", CampusReportViewSet, basename="campus-report")
router.register(
    "academic-calendars",
    AcademicCalendarViewSet,
    basename="academic-calendar",
)
router.register("campus-events", CampusEventViewSet, basename="campus-event")
router.register("student-clubs", StudentClubViewSet, basename="student-club")
router.register("campus-unions", CampusUnionViewSet, basename="campus-unions")
router.register(
    "student-club-events",
    StudentClubEventViewSet,
    basename="student-club-event",
)

urlpatterns = [
    path("campus-info", CampusInfoAPIView.as_view(), name="campus-info"),
    path(
        "campus-info/social-media-links/<int:pk>/delete",
        SocialMediaLinkDeleteAPIView.as_view(),
    ),
    path(
        "campus-events/<int:event_id>/gallery/<int:gallery_id>",
        CampusEventGalleryDestroyAPIView.as_view(),
        name="campus-events-gallery-destroy",
    ),
    path(
        "student-club-events/<int:event_id>/gallery/<int:gallery_id>",
        StudentClubEventGalleryDestroyAPIView.as_view(),
        name="student-club-events-gallery-destroy",
    ),
    # Listing APIs
    path(
        "campus-reports/fiscal-sessions",
        FiscalSessionBSForCampusReportListAPIView.as_view(),
    ),
    path("", include(router.urls)),
]
