from django.urls import include, path
from rest_framework import routers

from .views import *
from .viewsets import *

router = routers.DefaultRouter()
router.register(r"main", DepartmentViewSet)
router.register(r"projects", ProjectViewSet)
router.register(r"question-banks", QuestionBankViewSet)
router.register(r"plans-policies", PlansPolicyViewSet)
router.register(r"students", StudentViewSet)
router.register(r"faqs", FAQViewSet)
router.register(r"blogs", BlogViewSet)
router.register(r"programs", ProgramsViewSet)

router.register(r"staffmembers", StaffMemberViewSet)
router.register(r"designations", DesignationViewSet)
router.register(r"societies", SocietyViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("staffs/search/", StaffSearchViews.as_view()),
]
