from django.shortcuts import render
from django.urls import path, include
from rest_framework import routers
from .viewsets import HomeViewSet, DepartmentSocialMediaViewSet, StaffMemberSocialMediaViewSet, SocietySocialMediaViewSet

router = routers.DefaultRouter()
router.register(r'home', HomeViewSet)
router.register(r'department-social-media', DepartmentSocialMediaViewSet)
router.register(r'staff-member-social-media', StaffMemberSocialMediaViewSet)
router.register(r'society-social-media', SocietySocialMediaViewSet)

urlpatterns = [
    path('', include(router.urls)),

]