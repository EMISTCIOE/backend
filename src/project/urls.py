from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProjectTagViewSet, ProjectViewSet

router = DefaultRouter(trailing_slash=False)

router.register("projects", ProjectViewSet, basename="project")
router.register("project-tags", ProjectTagViewSet, basename="project-tag")

urlpatterns = [
    path("", include(router.urls)),
]
