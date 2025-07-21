from django.urls import include, path
from rest_framework.routers import DefaultRouter
from src.website.public.views import CampusInfoPublicView

router = DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
    path("campus-info/", CampusInfoPublicView.as_view(), name="campus-info"),
]
