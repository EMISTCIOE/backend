from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ResearchCategoryViewSet, ResearchViewSet

router = DefaultRouter(trailing_slash=False)

router.register("research", ResearchViewSet, basename="research")
router.register(
    "research-categories",
    ResearchCategoryViewSet,
    basename="research-category",
)

urlpatterns = [
    path("", include(router.urls)),
]
