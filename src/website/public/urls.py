from django.urls import include, path

# Rest Framework Import
from rest_framework.routers import DefaultRouter

# Project Import
from src.website.public.views import PublicCampusInfoRetrieveAPIView

router = DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
    path("campus-info", PublicCampusInfoRetrieveAPIView.as_view(), name="campus-info"),
]
