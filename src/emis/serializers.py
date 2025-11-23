"""
EMIS API serializers for VPS info, hardware, and email reset requests.
"""

import re

from rest_framework import serializers

from .models import (
    EmailResetRequest,
    EMISDownload,
    EMISHardware,
    EMISNotice,
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
            "service_key",
            "port",
            "protocol",
            "service_type",
            "domain",
            "is_ssl_enabled",
            "healthcheck_endpoint",
            "healthcheck_expectation",
            "version",
            "deploy_strategy",
            "auto_restart",
            "maintained_by",
            "status",
            "last_deployed_at",
            "description",
            "metadata",
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
        metadata = validated_data.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            raise serializers.ValidationError({"metadata": "Metadata must be a JSON object"})
        return super().update(instance, validated_data)


class EMISVPSInfoSerializer(serializers.ModelSerializer):
    services = EMISVPSServiceSerializer(many=True, read_only=True)
    services_count = serializers.SerializerMethodField()

    class Meta:
        model = EMISVPSInfo
        fields = [
            "id",
            "vps_name",
            "slug",
            "provider",
            "environment",
            "status",
            "health_status",
            "ip_address",
            "private_ip_address",
            "location",
            "ram_gb",
            "cpu_cores",
            "storage_gb",
            "storage_type",
            "bandwidth_tb",
            "ssh_port",
            "operating_system",
            "kernel_version",
            "monitoring_url",
            "last_health_check_at",
            "tags",
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
            "slug",
            "services",
            "services_count",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_active",
            "last_health_check_at",
        ]

    def get_services_count(self, obj):
        return obj.services.filter(is_active=True).count()

    def validate_tags(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Tags must be a list")
        for tag in value:
            if not isinstance(tag, str):
                raise serializers.ValidationError("Tags must contain strings only")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        validated_data["updated_by"] = user
        return super().update(instance, validated_data)

    def validate_metadata(self, value):
        if value is not None and not isinstance(value, dict):
            raise serializers.ValidationError("Metadata must be a JSON object")
        return value


class EMISHardwareSerializer(serializers.ModelSerializer):
    endpoints = serializers.JSONField(required=False)
    specifications = serializers.JSONField(required=False)
    thumbnail_image = serializers.ImageField(required=False)

    class Meta:
        model = EMISHardware
        fields = [
            "id",
            "name",
            "asset_tag",
            "hardware_type",
            "manufacturer",
            "model_number",
            "serial_number",
            "ip_address",
            "location",
            "environment",
            "status",
            "responsible_team",
            "purchase_date",
            "warranty_expires_at",
            "power_draw_watts",
            "rack_unit",
            "thumbnail_image",
            "endpoints",
            "specifications",
            "description",
            "metadata",
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


class EMISDownloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EMISDownload
        fields = [
            "id",
            "uuid",
            "title",
            "description",
            "category",
            "file",
            "link_url",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_active",
        ]
        read_only_fields = [
            "id",
            "uuid",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_active",
        ]

    def validate(self, attrs):
        file = attrs.get("file") or getattr(self.instance, "file", None)
        link_url = attrs.get("link_url") or getattr(self.instance, "link_url", None)
        if not file and not link_url:
            raise serializers.ValidationError("Either a file or link URL is required.")
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["updated_by"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        validated_data["updated_by"] = user
        return super().update(instance, validated_data)


class EMISNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EMISNotice
        fields = [
            "id",
            "uuid",
            "slug",
            "title",
            "summary",
            "body",
            "category",
            "severity",
            "published_at",
            "is_published",
            "attachment",
            "external_url",
            "views",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_active",
        ]
        read_only_fields = [
            "id",
            "uuid",
            "slug",
            "views",
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
    requestSequence = serializers.IntegerField(source='request_sequence', read_only=True)
    requestsRemaining = serializers.SerializerMethodField()
    processedByName = serializers.SerializerMethodField()
    fullName = serializers.CharField(source='full_name')
    rollNumber = serializers.CharField(source='roll_number')
    birthDate = serializers.DateField(source='birth_date')
    primaryEmail = serializers.EmailField(source='primary_email')
    secondaryEmail = serializers.EmailField(source='secondary_email')
    phoneNumber = serializers.CharField(source='phone_number')
    processedAt = serializers.DateTimeField(source='processed_at', read_only=True)
    processedBy = serializers.PrimaryKeyRelatedField(source='processed_by', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)

    def to_internal_value(self, data):
        """
        Convert camelCase input to snake_case for model fields
        """
        # Accept both camelCase and snake_case input keys.
        # The serializer defines camelCase fields (e.g. `fullName = serializers.CharField(source='full_name')`)
        # so we want to pass camelCase keys to DRF's `to_internal_value`.
        # Build mapping Camel -> snake and its inverse so we can convert snake_case -> camelCase.
        field_mapping = {
            'fullName': 'full_name',
            'rollNumber': 'roll_number',
            'birthDate': 'birth_date',
            'primaryEmail': 'primary_email',
            'secondaryEmail': 'secondary_email',
            'phoneNumber': 'phone_number',
        }

        inverse_mapping = {v: k for k, v in field_mapping.items()}

        converted = {}
        for key, value in data.items():
            # If client already sent camelCase keys that the serializer expects, keep them.
            if key in field_mapping:
                converted[key] = value
            # If client sent snake_case keys, convert them to the camelCase serializer field name.
            elif key in inverse_mapping:
                converted[inverse_mapping[key]] = value
            else:
                # Leave other keys as-is (they may be additional fields/metadata)
                converted[key] = value

        return super().to_internal_value(converted)

    class Meta:
        model = EmailResetRequest
        fields = [
            "id",
            "fullName",
            "rollNumber", 
            "birthDate",
            "primaryEmail",
            "secondaryEmail",
            "phoneNumber",
            "status",
            "requestSequence",
            "requestsRemaining",
            "processedAt",
            "processedBy",
            "processedByName",
            "notes",
            "createdAt",
            "updatedAt",
        ]
        read_only_fields = [
            "id",
            "requestSequence",
            "requestsRemaining",
            "processedByName",
            "processedAt",
            "processedBy",
            "createdAt",
            "updatedAt",
        ]

    def get_processedByName(self, obj):
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
        from django.contrib.auth import get_user_model
        
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
        if user.is_anonymous:
            # For anonymous users (students requesting email reset), 
            # use a system user or create one if it doesn't exist
            User = get_user_model()
            system_user, created = User.objects.get_or_create(
                username="system_email_reset",
                defaults={
                    "email": "system@tcioe.edu.np",
                    "first_name": "System",
                    "last_name": "Email Reset",
                    "is_active": True,
                    "is_staff": False,
                }
            )
            user = system_user
            
        validated_data["created_by"] = user
        validated_data["updated_by"] = user
        return super().create(validated_data)

    def get_requestsRemaining(self, obj):
        return max(0, 10 - obj.request_sequence)
