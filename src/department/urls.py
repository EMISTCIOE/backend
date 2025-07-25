from django.urls import include, path
from rest_framework import routers

from .views import (
    DepartmentViewSet,
    AcademicProgramViewSet,
    DepartmentDownloadViewSet,
    DepartmentEventViewSet,
    DepartmentPlanAndPolicyViewSet,
    StaffMemberViewSet,
)

router = routers.DefaultRouter()

# Register all viewsets
router.register("departments", DepartmentViewSet, basename="department")
router.register(
    "academic-programs", AcademicProgramViewSet, basename="academic-program"
)
router.register(
    "department-downloads", DepartmentDownloadViewSet, basename="department-download"
)
router.register(
    "department-events", DepartmentEventViewSet, basename="department-event"
)
router.register(
    "department-plans-policies",
    DepartmentPlanAndPolicyViewSet,
    basename="department-plan-and-policy",
)
router.register("staff-members", StaffMemberViewSet, basename="staff-member")

urlpatterns = [
    path("", include(router.urls)),
]
