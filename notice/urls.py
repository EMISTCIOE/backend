from django.shortcuts import render
from django.urls import path, include
from rest_framework import routers
from .viewsets import NoticeViewSet, NoticeTypeViewSet, NoticeCategoryViewSet

router = routers.DefaultRouter()
router.register(r'notices', NoticeViewSet)
router.register(r'types',NoticeTypeViewSet)
router.register(r'categories',NoticeCategoryViewSet)
urlpatterns = [
    path('', include(router.urls)),
]