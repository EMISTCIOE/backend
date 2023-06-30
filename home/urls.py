from django.shortcuts import render
from django.urls import path, include
from rest_framework import routers
from .viewsets import HomeViewSet, SocialMediaViewSet, ResourceViewSet, UnitViewSet

router = routers.DefaultRouter()
router.register(r'home', HomeViewSet)
router.register(r'socialmedia', SocialMediaViewSet)
router.register(r'resources', ResourceViewSet)
router.register(r'units', UnitViewSet)



urlpatterns = [
    path('', include(router.urls)),

]