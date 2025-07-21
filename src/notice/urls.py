from django.urls import path
from rest_framework.routers import DefaultRouter

from .listing_apis.views import (
    AuthorForNoticeListAPIView,
    CategoryForNoticeListAPIView,
    DepartmentForNoticeListAPIView,
)
from .views import NoticeStatusUpdateAPIView, NoticeViewSet

router = DefaultRouter(trailing_slash=False)

router.register("notices", NoticeViewSet, basename="notices")


urlpatterns = [
    path("notices/<int:id>/update-status", NoticeStatusUpdateAPIView.as_view()),
]

list_urls = [
    path("notices/departments", DepartmentForNoticeListAPIView.as_view()),
    path("notices/categories", CategoryForNoticeListAPIView.as_view()),
    path("notices/authors", AuthorForNoticeListAPIView.as_view()),
]

urlpatterns = [*list_urls, *router.urls]
