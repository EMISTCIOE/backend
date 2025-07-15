from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView

# Project Imports
from src.user.models import UserRole
from src.user.permissions import UserSetupPermission
from .serializers import RoleForUserSerializer


class RoleForUserView(ListAPIView):
    permission_classes = [UserSetupPermission]
    queryset = UserRole.objects.filter(is_active=True, is_cms_role=True)
    serializer_class = RoleForUserSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_fields = ["id", "name", "codename"]
    search_fields = ["id", "name"]
    ordering_fields = ["id", "name"]
    ordering = ["name"]
