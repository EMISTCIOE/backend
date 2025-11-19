"""
EMIS API router configuration.
"""

from rest_framework.routers import DefaultRouter

from .views import (
    EmailResetRequestViewSet,
    EMISHardwareViewSet,
    EMISVPSInfoViewSet,
    EMISVPSServiceViewSet,
)

router = DefaultRouter(trailing_slash=False)
router.register("vps-info", EMISVPSInfoViewSet, basename="emis-vps-info")
router.register("vps-services", EMISVPSServiceViewSet, basename="emis-vps-services")
router.register("hardware", EMISHardwareViewSet, basename="emis-hardware")
router.register(
    "email-reset",
    EmailResetRequestViewSet,
    basename="emis-email-reset",
)

urlpatterns = router.urls
