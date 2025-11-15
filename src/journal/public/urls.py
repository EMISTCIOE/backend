from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PublicArticleViewSet

router = DefaultRouter(trailing_slash=False)
router.register("articles", PublicArticleViewSet, basename="public-article")

urlpatterns = [
    path("", include(router.urls)),
]
