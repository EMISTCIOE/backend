from django.urls import include, path
from rest_framework import routers

from .views import (
    AcademicProgramViewSet,
    DepartmentDownloadViewSet,
    DepartmentPlanAndPolicyViewSet,
    DepartmentSocialMediaDestroyAPIView,
    DepartmentViewSet,
)

router = routers.DefaultRouter(trailing_slash=False)

# Register all viewsets
router.register("departments", DepartmentViewSet, basename="department")
router.register(
    "academic-programs",
    AcademicProgramViewSet,
    basename="academic-program",
)
router.register(
    "department-downloads",
    DepartmentDownloadViewSet,
    basename="department-download",
)
router.register(
    "department-plans-policies",
    DepartmentPlanAndPolicyViewSet,
    basename="department-plan-and-policy",
)

urlpatterns = [
    path(
        "departments/<int:department_id>/social-link/<int:social_link_id>",
        DepartmentSocialMediaDestroyAPIView.as_view(),
        name="department-social-link-destroy",
    ),
    path("", include(router.urls)),
]
