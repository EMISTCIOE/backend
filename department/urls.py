from django.urls import path, include
from rest_framework import routers
from .viewsets import *
from .views import *

router = routers.DefaultRouter()
router.register(r'main', DepartmentViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'question-banks', QuestionBankViewSet)
router.register(r'plans-policies', PlansPolicyViewSet)
router.register(r'students', StudentViewSet)
router.register(r'faqs', FAQViewSet)
router.register(r'blogs', BlogViewSet)
router.register(r'programs', ProgramsViewSet)
router.register(r'semesters', SemesterViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'staffmembers', StaffMemberViewSet)
router.register(r'designations', DesignationViewSet)
router.register(r'societies', SocietyViewSet)
router.register(r'routines', RoutineViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('subjects/search/', DepartmentSubjects.as_view()),
    path('staffs/search/', StaffSearchViews.as_view()),
]
