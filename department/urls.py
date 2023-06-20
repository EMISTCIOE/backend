from django.shortcuts import render
from django.urls import path, include
from rest_framework import routers
from .viewsets import DepartmentViewSet, DesignationViewSet, StaffMemberViewSet, SocietyViewSet

router = routers.DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'designations', DesignationViewSet)
router.register(r'staffmembers', StaffMemberViewSet)
router.register(r'societies', SocietyViewSet)

urlpatterns = [
    path('', include(router.urls)),
]