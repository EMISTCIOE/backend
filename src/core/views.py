from django.utils.translation import gettext as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ModelViewSet

# Project Imports
from .models import EmailConfig
from .permissions import EmailConfigPermission
from .serializers import (
    EmailConfigCreateSerializer,
    EmailConfigListSerializer,
    EmailConfigPatchSerializer,
    EmailConfigRetrieveSerializer,
)


class EmailConfigViewSet(ModelViewSet):
    """Email Config ViewSet"""

    permission_classes = [EmailConfigPermission]
    queryset = EmailConfig.objects.filter(is_archived=False)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    serializer_class = EmailConfigListSerializer
    filterset_fields = ["email_type"]
    search_fields = ["email_type", "default_from_email"]
    ordering = ["-created_at"]
    ordering_fields = ["id", "created_at"]
    http_method_names = ["get", "head", "options", "post", "patch"]

    def get_serializer_class(self):
        serializer_class = EmailConfigListSerializer
        if self.request.method == "GET":
            if self.action == "list":
                serializer_class = EmailConfigListSerializer
            else:
                serializer_class = EmailConfigRetrieveSerializer
        if self.request.method == "POST":
            serializer_class = EmailConfigCreateSerializer
        if self.request.method == "PATCH":
            serializer_class = EmailConfigPatchSerializer

        return serializer_class
