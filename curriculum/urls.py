from django.urls import path, include
from rest_framework import routers
from .viewsets import *
from .views import *

router = routers.DefaultRouter()

router.register(r"routines", RoutineViewSet)
router.register(r"subjects", SubjectViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("subjects/search/", DepartmentSubjects.as_view()),
]
