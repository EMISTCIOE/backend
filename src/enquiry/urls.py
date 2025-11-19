"""
Enquiry URLs
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import MeetingEnquiryViewSet

router = DefaultRouter(trailing_slash=False)
router.register("meeting-requests", MeetingEnquiryViewSet, basename="meeting-requests")

urlpatterns = router.urls
