from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Project Imports
from src.website.public.views import PublicCampusInfoRetrieveAPIView

router = DefaultRouter()

urlpatterns = [
    path("campus-info", PublicCampusInfoRetrieveAPIView.as_view(), name="campus-info"),
    path("", include(router.urls)),
]
