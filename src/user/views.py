# Django Imports
import django_filters
from django.utils import timezone
from django_filters.filterset import FilterSet
from django_filters.rest_framework import DjangoFilterBackend

# Rest Framework Imports
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ModelViewSet

# Project Imports
from src.libs.utils import set_binary_files_null_if_empty

from .messages import USER_ARCHIVED
from .models import User
from .permissions import UserSetupPermission
from .serializers import (
    UserListSerializer,
    UserPatchSerializer,
    UserRegisterSerializer,
    UserRetrieveSerializer,
)


class FilterForUserViewSet(FilterSet):
    """Filters For User ViewSet"""

    username = django_filters.CharFilter(lookup_expr="iexact")
    date = django_filters.DateFromToRangeFilter(field_name="date_joined")

    class Meta:
        model = User
        fields = ["id", "username", "email", "phone_no", "roles", "date"]


class UserViewSet(ModelViewSet):
    """
    ViewSet for managing CRUD operations for User.
    """

    permission_classes = [UserSetupPermission]
    filterset_class = FilterForUserViewSet
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["phone_no", "username", "email", "first_name", "last_name"]
    ordering_fields = ["-id", "first_name"]
    http_method_names = ["options", "head", "get", "patch", "post"]

    def get_queryset(self):
        return User.objects.filter(
            is_superuser=False,
            is_staff=False,
            roles__is_cms_role=True,
            roles__is_active=True,
            is_archived=False,
        ).distinct()

    def get_serializer_class(self):
        serializer_class = UserListSerializer
        if self.request.method == "GET":
            if self.action == "list":
                serializer_class = UserListSerializer
            else:
                serializer_class = UserRetrieveSerializer

        if self.request.method == "POST":
            serializer_class = UserRegisterSerializer
        elif self.request.method == "PATCH":
            serializer_class = UserPatchSerializer
        return serializer_class

    def create(self, request, *args, **kwargs):
        # set blank file fields to None/null
        file_fields = ["photo"]
        if file_fields:
            set_binary_files_null_if_empty(file_fields, request.data)

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # set blank file fields to None/null
        file_fields = ["photo"]
        if file_fields:
            set_binary_files_null_if_empty(file_fields, request.data)

        return super().update(request, *args, **kwargs)


class UserArchiveView(generics.DestroyAPIView):
    """User Archive View"""

    permission_classes = [UserSetupPermission]
    lookup_url_kwarg = "user_id"
    lookup_field = "id"

    def get_queryset(self):
        return User.objects.filter(
            is_superuser=False,
            is_staff=False,
            roles__is_cms_role=True,
            roles__is_active=True,
            is_archived=False,
        ).distinct()

    def perform_destroy(self, instance):
        instance.is_archived = True
        instance.updated_at = timezone.now()

        instance.save()

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        response.data = {"message": USER_ARCHIVED}
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
