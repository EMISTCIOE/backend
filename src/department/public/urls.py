from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Project Imports
from src.department.public.views import (
    PublicDepartmentDownloadListAPIView,
    PublicDepartmentEventGalleryListAPIView,
    PublicDepartmentEventListAPIView,
    PublicDepartmentListAPIView,
    PublicDepartmentPlanPolicyListAPIView,
    PublicDepartmentProgramListAPIView,
    PublicDepartmentRetrieveAPIView,
    PublicDepartmentStaffListAPIView,
)

router = DefaultRouter()

urlpatterns = [
    path(
        "departments",
        PublicDepartmentListAPIView.as_view(),
        name="public-department-list",
    ),
    path(
        "departments/<slug:slug>",
        PublicDepartmentRetrieveAPIView.as_view(),
        name="public-department-detail",
    ),
    path(
        "departments/<slug:slug>/staffs",
        PublicDepartmentStaffListAPIView.as_view(),
        name="public-department-staff-list",
    ),
    path(
        "departments/<slug:slug>/programs",
        PublicDepartmentProgramListAPIView.as_view(),
        name="public-department-program-list",
    ),
    path(
        "departments/<slug:slug>/downloads",
        PublicDepartmentDownloadListAPIView.as_view(),
        name="public-department-download-list",
    ),
    path(
        "departments/<slug:slug>/events",
        PublicDepartmentEventListAPIView.as_view(),
        name="public-department-event-list",
    ),
    path(
        "departments/events/<int:event_id>/gallery",
        PublicDepartmentEventGalleryListAPIView.as_view(),
        name="public-department-event-gallery",
    ),
    path(
        "departments/<slug:slug>/plans",
        PublicDepartmentPlanPolicyListAPIView.as_view(),
        name="public-department-plan-list",
    ),
    path("", include(router.urls)),
]
