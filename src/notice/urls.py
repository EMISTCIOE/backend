from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .listing_apis.views import (
    AuthorForNoticeListAPIView,
    CategoryForNoticeListAPIView,
    DepartmentForNoticeListAPIView,
)
from .views import NoticeViewSet

router = DefaultRouter(trailing_slash=False)

router.register("notices", NoticeViewSet, basename="notices")


urlpatterns = [
    path("notices/departments", DepartmentForNoticeListAPIView.as_view()),
    path("notices/categories", CategoryForNoticeListAPIView.as_view()),
    path("notices/authors", AuthorForNoticeListAPIView.as_view()),
    path("", include(router.urls)),
]
