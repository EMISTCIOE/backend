from rest_framework.generics import ListAPIView
from rest_framework.filters import OrderingFilter, SearchFilter

from src.core.models import FiscalSessionBS
from src.website.permissions import CampusReportPermission
from .serializers import FiscalSessionBSForCampusReportListSerializer


class FiscalSessionBSForCampusReportListAPIView(ListAPIView):
    permission_classes = [CampusReportPermission]
    queryset = FiscalSessionBS.objects.filter(is_active=True)
    serializer_class = FiscalSessionBSForCampusReportListSerializer
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ["session_short", "session_full"]
    ordering_fields = ["session_short", "session_full"]
    ordering = ["-session_short"]
