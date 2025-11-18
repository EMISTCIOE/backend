from django.urls import include, path
from rest_framework.routers import DefaultRouter

from src.contact.views import PhoneNumberViewSet

router = DefaultRouter()
router.register(r"phone-numbers", PhoneNumberViewSet, basename="phonenumber")

urlpatterns = [
    path("", include(router.urls)),
]
