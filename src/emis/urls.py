"""
EMIS URLs
"""

from rest_framework.routers import DefaultRouter

from .views import VPSConfigurationViewSet

router = DefaultRouter(trailing_slash=False)
router.register("vps-config", VPSConfigurationViewSet, basename="vps-config")

urlpatterns = router.urls
