from django.shortcuts import render
from django.urls import path, include
from rest_framework import routers
from .viewsets import HomeViewSet, SocialMediaViewSet

router = routers.DefaultRouter()
router.register(r'home', HomeViewSet)
router.register(r'socialmedia', SocialMediaViewSet)


urlpatterns = [
    path('', include(router.urls)),

]