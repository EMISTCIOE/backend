from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import AuditInfoModel, PublicAuditInfoModel


class AbstractInfoRetrieveSerializer(ModelSerializer):
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()

    class Meta:
        model = AuditInfoModel
        fields = [
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "is_active",
        ]

    def get_created_by(self, obj) -> str:
        user = obj.created_by
        return user.get_full_name() or user.username if user else ""

    def get_updated_by(self, obj) -> str:
        user = obj.updated_by
        return user.get_full_name() or user.username if user else ""


class PublicAbstractInfoRetrieveSerializer(ModelSerializer):
    class Meta:
        model = PublicAuditInfoModel
        fields = ["created_at", "updated_at", "is_active"]
