from rest_framework import serializers

from src.core.models import FiscalSessionBS


class FiscalSessionBSForCampusReportListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiscalSessionBS
        fields = ["id", "session_full", "session_short"]
