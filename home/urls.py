from django.shortcuts import render
from django.urls import path, include
from rest_framework import routers
from .viewsets import HomeViewSet

router = routers.DefaultRouter()
router.register(r'home', HomeViewSet)


urlpatterns = [
    path('', include(router.urls)),

]