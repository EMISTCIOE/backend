from django.urls import include, path
from rest_framework import routers

from .views import *
from .viewsets import *

router = routers.DefaultRouter()

router.register(r"routines", RoutineViewSet)
router.register(r"subjects", SubjectViewSet)
# router.register(r"suggestion", SuggestionViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("subjects/search/", DepartmentSubjects.as_view()),
    path("suggestions/", suggestion_create_view, name="suggestion_create"),
]
