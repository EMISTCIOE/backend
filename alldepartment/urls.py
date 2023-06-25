from django.urls import path, include
from .viewsets import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'dep', DepartmentViewSet)
# router.register(r'designations', DesignationViewSet)
# router.register(r'staffmembers', StaffMemberViewSet)
# router.register(r'societies', SocietyViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
