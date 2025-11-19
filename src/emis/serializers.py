"""
EMIS API serializers for VPS info, hardware, and email reset requests.
"""

import re

from rest_framework import serializers

from .models import (
    EmailResetRequest,
    EMISHardware,
    EMISVPSInfo,
    PRIMARY_EMAIL_DOMAIN,
    ROLL_NUMBER_PATTERN,
)


class EMISVPSInfoSerializer(serializers.ModelSerializer):
    affiliated_ports = serializers.JSONField(required=False)

    class Meta:
        model = EMISVPSInfo
        fields = [
            "id",
            "vps_label",
            "ip_address",
            "description",
            "notes",
            "affiliated_ports",
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
        instance.updated_by = self.context["request"].user
        return super().update(instance, validated_data)


class EMISHardwareSerializer(serializers.ModelSerializer):
    endpoints = serializers.JSONField(required=False)

    class Meta:
        model = EMISHardware
        fields = [
            "id",
            "name",
            "hardware_type",
            "ip_address",
            "location",
            "endpoints",
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
        instance.updated_by = self.context["request"].user
        return super().update(instance, validated_data)


class EmailResetRequestSerializer(serializers.ModelSerializer):
    request_sequence = serializers.IntegerField(read_only=True)
    requests_remaining = serializers.SerializerMethodField()

    class Meta:
        model = EmailResetRequest
        fields = [
            "id",
            "full_name",
            "roll_number",
            "birth_date",
            "primary_email",
            "secondary_email",
            "request_sequence",
            "requests_remaining",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "request_sequence",
            "requests_remaining",
            "created_at",
        ]

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
