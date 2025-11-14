from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PublicProjectViewSet, PublicProjectTagViewSet

router = DefaultRouter(trailing_slash=False)

router.register('projects', PublicProjectViewSet, basename='public-project')
router.register('project-tags', PublicProjectTagViewSet, basename='public-project-tag')

urlpatterns = [
    path('', include(router.urls)),
]