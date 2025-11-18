from django.urls import path
from rest_framework import routers

from .views import DashboardStatsView, EmailConfigViewSet

router = routers.DefaultRouter(trailing_slash=False)

router.register("email-configs", EmailConfigViewSet)


list_urls = [
    path("dashboard-stats", DashboardStatsView.as_view(), name="dashboard-stats"),
]

urlpatterns = [*list_urls, *router.urls]
