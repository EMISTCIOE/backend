"""
EMIS API serializers for VPS info, hardware, and email reset requests.
"""

import re

from rest_framework import serializers

from .models import (
    EmailResetRequest,
    EMISHardware,
    EMISVPSInfo,
    EMISVPSService,
    PRIMARY_EMAIL_DOMAIN,
    ROLL_NUMBER_PATTERN,
)


class EMISVPSServiceSerializer(serializers.ModelSerializer):
    url = serializers.ReadOnlyField()

    class Meta:
        model = EMISVPSService
        fields = [
            "id",
            "vps",
            "name",
            "port",
            "service_type",
            "domain",
            "is_ssl_enabled",
            "description",
            "url",
            "created_at",
            "updated_at",
            "is_active",
        ]
        read_only_fields = [
            "id",
            "url",
            "created_at",
            "updated_at",
            "is_active",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        validated_data["updated_by"] = user
        return super().update(instance, validated_data)


class EMISVPSInfoSerializer(serializers.ModelSerializer):
    services = EMISVPSServiceSerializer(many=True, read_only=True)
    services_count = serializers.SerializerMethodField()

    class Meta:
        model = EMISVPSInfo
        fields = [
            "id",
            "vps_name",
            "ip_address",
            "ram_gb",
            "cpu_cores",
            "storage_gb",
            "description",
            "notes",
            "services",
            "services_count",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_active",
        ]
        read_only_fields = [
            "id",
            "services",
            "services_count",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_active",
        ]

    def get_services_count(self, obj):
        return obj.services.filter(is_active=True).count()

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        validated_data["updated_by"] = user
        return super().update(instance, validated_data)

    def update(self, instance, validated_data):
        instance.updated_by = self.context["request"].user
        return super().update(instance, validated_data)


class EMISHardwareSerializer(serializers.ModelSerializer):
    endpoints = serializers.JSONField(required=False)
    specifications = serializers.JSONField(required=False)
    thumbnail_image = serializers.ImageField(required=False)

    class Meta:
        model = EMISHardware
        fields = [
            "id",
            "name",
            "hardware_type",
            "ip_address",
            "location",
            "thumbnail_image",
            "endpoints",
            "specifications",
            "description",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_active",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_active",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        validated_data["updated_by"] = user
        return super().update(instance, validated_data)


class EmailResetRequestSerializer(serializers.ModelSerializer):
    request_sequence = serializers.IntegerField(read_only=True)
    requests_remaining = serializers.SerializerMethodField()
    processed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = EmailResetRequest
        fields = [
            "id",
            "full_name",
            "roll_number",
            "birth_date",
            "primary_email",
            "secondary_email",
            "phone_number",
            "status",
            "request_sequence",
            "requests_remaining",
            "processed_at",
            "processed_by",
            "processed_by_name",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "request_sequence",
            "requests_remaining",
            "processed_by_name",
            "created_at",
            "updated_at",
        ]

    def get_processed_by_name(self, obj):
        if obj.processed_by:
            return f"{obj.processed_by.first_name} {obj.processed_by.last_name}".strip()
        return None

    def validate_roll_number(self, value):
        normalized = value.strip().upper()
        if not re.match(ROLL_NUMBER_PATTERN, normalized):
            raise serializers.ValidationError(
                "Roll number must follow the format THA080BCT002.",
            )
        return normalized

    def validate_primary_email(self, value):
        normalized = value.strip().lower()
        if not normalized.endswith(PRIMARY_EMAIL_DOMAIN):
            raise serializers.ValidationError(
                f"Primary email must end with {PRIMARY_EMAIL_DOMAIN}.",
            )
        return normalized

    def validate_secondary_email(self, value):
        return value.strip().lower()

    def create(self, validated_data):
        roll = validated_data["roll_number"]
        existing_count = EmailResetRequest.objects.filter(
            roll_number__iexact=roll,
        ).count()
        if existing_count >= 10:
            raise serializers.ValidationError(
                "Maximum of 10 email reset requests has been reached for this roll number.",
            )
        validated_data["request_sequence"] = existing_count + 1
        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user
        return super().create(validated_data)

    def get_requests_remaining(self, obj):
        return max(0, 10 - obj.request_sequence)
