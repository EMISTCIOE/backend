from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from src.emis.models import EMISDownload, EMISNotice

from .serializers import PublicEMISDownloadSerializer, PublicEMISNoticeSerializer


class PublicEMISDownloadListAPIView(generics.ListAPIView):
    """Public listing of EMIS downloads grouped by category."""

    permission_classes = [AllowAny]
    serializer_class = PublicEMISDownloadSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "title"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = EMISDownload.objects.filter(is_active=True)
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)
        return queryset


class PublicEMISNoticeListAPIView(generics.ListAPIView):
    """Public listing of EMIS notices (security, maintenance, releases)."""

    permission_classes = [AllowAny]
    serializer_class = PublicEMISNoticeSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "summary", "body"]
    ordering_fields = ["published_at", "severity"]
    ordering = ["-published_at"]

    def get_queryset(self):
        queryset = EMISNotice.objects.filter(is_active=True, is_published=True)
        category = self.request.query_params.get("category")
        severity = self.request.query_params.get("severity")
        if category:
            queryset = queryset.filter(category=category)
        if severity:
            queryset = queryset.filter(severity=severity)
        return queryset


class PublicEMISNoticeRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve a single EMIS notice by slug or UUID."""

    permission_classes = [AllowAny]
    serializer_class = PublicEMISNoticeSerializer

    def get_object(self):
        identifier = self.kwargs.get("notice_id")
        queryset = EMISNotice.objects.filter(is_active=True, is_published=True)
        if not identifier:
            raise Http404

        try:
            # Try UUID lookup first
            return queryset.get(uuid=identifier)
        except (ValueError, EMISNotice.DoesNotExist):
            return get_object_or_404(queryset, slug=identifier)


class PublicEMISNoticeSetViewedAPIView(generics.UpdateAPIView):
    """Increment view count when a notice is opened."""

    permission_classes = [AllowAny]
    http_method_names = ["patch"]

    def patch(self, request, *args, **kwargs):
        identifier = kwargs.get("notice_id")
        queryset = EMISNotice.objects.filter(is_active=True, is_published=True)
        try:
            notice = queryset.get(uuid=identifier)
        except (ValueError, EMISNotice.DoesNotExist):
            notice = get_object_or_404(queryset, slug=identifier)
        notice.increment_views()
        return Response(
            {"message": "View recorded", "views": notice.views},
            status=status.HTTP_200_OK,
        )
