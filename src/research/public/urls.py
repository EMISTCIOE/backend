from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PublicResearchCategoryViewSet, PublicResearchViewSet

router = DefaultRouter(trailing_slash=False)

router.register("research", PublicResearchViewSet, basename="public-research")
router.register(
    "research-categories",
    PublicResearchCategoryViewSet,
    basename="public-research-category",
)

urlpatterns = [
    path("", include(router.urls)),
]
