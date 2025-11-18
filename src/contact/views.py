# Django Imports
import django_filters
from django_filters.filterset import FilterSet
from django_filters.rest_framework import DjangoFilterBackend

# Rest Framework Imports
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

# Project Imports
from src.contact.models import PhoneNumber
from src.contact.serializers import (
    PhoneNumberCreateSerializer,
    PhoneNumberListSerializer,
    PhoneNumberPublicSerializer,
    PhoneNumberRetrieveSerializer,
    PhoneNumberUpdateSerializer,
)


class PhoneNumberFilterSet(FilterSet):
    """Filters for Phone Number ViewSet"""

    class Meta:
        model = PhoneNumber
        fields = ["is_active", "contact_type", "department"]


class PhoneNumberViewSet(ModelViewSet):
    """
    ViewSet for managing CRUD operations for Phone Numbers.
    """

    queryset = PhoneNumber.objects.filter(is_active=True).order_by(
        "display_order",
        "name",
    )
    permission_classes = [IsAuthenticated]
    filterset_class = PhoneNumberFilterSet
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["name", "phone_number", "description", "department__name"]
    ordering_fields = ["display_order", "name", "contact_type", "created_at"]
    ordering = ["display_order", "name"]

    def get_serializer_class(self):
        if self.action == "list":
            return PhoneNumberListSerializer
        elif self.action == "retrieve":
            return PhoneNumberRetrieveSerializer
        elif self.action == "create":
            return PhoneNumberCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return PhoneNumberUpdateSerializer
        return PhoneNumberListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Soft delete by setting is_active to False"""
        instance = self.get_object()
        instance.is_active = False
        instance.updated_by = request.user
        instance.save()
        return Response(
            {"message": "Phone number deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(detail=False, methods=["post"])
    def bulk_delete(self, request):
        """Bulk soft delete phone numbers"""
        ids = request.data.get("ids", [])
        if not ids:
            return Response(
                {"error": "No IDs provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_count = PhoneNumber.objects.filter(id__in=ids, is_active=True).update(
            is_active=False,
            updated_by=request.user,
        )

        return Response(
            {"message": f"Successfully deleted {updated_count} phone numbers"},
            status=status.HTTP_200_OK,
        )


class PhoneNumberPublicListView(ListAPIView):
    """
    Public API for phone numbers - accessible without authentication
    Used by frontend to display contact information
    Only shows active records that have phone numbers (no empty entries)
    """

    queryset = (
        PhoneNumber.objects.filter(is_active=True)
        .exclude(phone_number__isnull=True)
        .exclude(phone_number__exact="")
        .order_by("display_order", "name")
    )
    serializer_class = PhoneNumberPublicSerializer
    permission_classes = [AllowAny]
    filter_backends = (OrderingFilter,)
    ordering_fields = ["display_order", "name", "contact_type"]
    ordering = ["display_order", "name"]
