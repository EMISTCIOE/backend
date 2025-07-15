from django.shortcuts import render
from django.urls import include, path
from rest_framework import routers

from .views import NoticeSearchView
from .viewsets import NoticeCategoryViewSet, NoticeTypeViewSet, NoticeViewSet

router = routers.DefaultRouter()
router.register(r"notices", NoticeViewSet)
router.register(r"types", NoticeTypeViewSet)
router.register(r"categories", NoticeCategoryViewSet)
urlpatterns = [
    path("", include(router.urls)),
    path("search/", NoticeSearchView.as_view(), name="notice-search"),
]
