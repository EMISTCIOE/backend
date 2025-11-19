"""
EMIS Serializers
"""

from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import OTPVerification, VPSConfiguration
from .utils import decrypt_password, encrypt_password, generate_otp


class VPSConfigurationListSerializer(serializers.ModelSerializer):
    """List VPS configurations (without password)"""

    services_count = serializers.SerializerMethodField()
    last_accessed_by_name = serializers.CharField(
        source="last_accessed_by.get_full_name",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = VPSConfiguration
        fields = [
            "id",
            "label",
            "ip_address",
            "port",
            "services_count",
            "last_accessed_by",
            "last_accessed_by_name",
            "last_accessed_at",
            "access_count",
            "is_active",
        ]

    def get_services_count(self, obj):
        return len(obj.services) if obj.services else 0


class VPSConfigurationDetailSerializer(serializers.ModelSerializer):
    """Detailed VPS configuration (without password)"""

    services_display = serializers.SerializerMethodField()

    class Meta:
        model = VPSConfiguration
        fields = [
            "id",
            "label",
            "ip_address",
            "port",
            "username",
            "services",
            "services_display",
            "description",
            "notes",
            "last_accessed_by",
            "last_accessed_at",
            "access_count",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_services_display(self, obj):
        return obj.get_services_display()


class VPSConfigurationCreateSerializer(serializers.ModelSerializer):
    """Create VPS configuration"""

    password = serializers.CharField(
        write_only=True,
        help_text="Plain password will be encrypted",
    )

    class Meta:
        model = VPSConfiguration
        fields = [
            "label",
            "ip_address",
            "port",
            "username",
            "password",
            "services",
            "description",
            "notes",
            "is_active",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        encrypted_password = encrypt_password(password)
        
        vps_config = VPSConfiguration.objects.create(
            encrypted_password=encrypted_password,
            created_by=self.context["request"].user,
            **validated_data,
        )
        return vps_config

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "message": f"VPS configuration '{instance.label}' created successfully.",
        }


class VPSConfigurationUpdateSerializer(serializers.ModelSerializer):
    """Update VPS configuration"""

    password = serializers.CharField(
        write_only=True,
        required=False,
        help_text="New password (optional)",
    )

    class Meta:
        model = VPSConfiguration
        fields = [
            "label",
            "ip_address",
            "port",
            "username",
            "password",
            "services",
            "description",
            "notes",
            "is_active",
        ]

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        
        if password:
            instance.encrypted_password = encrypt_password(password)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.updated_by = self.context["request"].user
        instance.save()
        return instance

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "message": f"VPS configuration '{instance.label}' updated successfully.",
        }


class OTPRequestSerializer(serializers.Serializer):
    """Request OTP for viewing password"""

    vps_config_id = serializers.IntegerField()

    def validate_vps_config_id(self, value):
        if not VPSConfiguration.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("VPS configuration not found.")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        vps_config = VPSConfiguration.objects.get(id=validated_data["vps_config_id"])
        
        # Generate OTP
        otp_code = generate_otp()
        expires_at = timezone.now() + timedelta(minutes=5)
        
        otp = OTPVerification.objects.create(
            user=user,
            vps_config=vps_config,
            otp_code=otp_code,
            expires_at=expires_at,
            created_by=user,
        )
        
        # TODO: Send OTP via email
        
        return otp

    def to_representation(self, instance):
        return {
            "message": "OTP has been sent to your email. It will expire in 5 minutes.",
            "otp_id": instance.id,
            # In development, show OTP (remove in production)
            "otp_code_dev": instance.otp_code,
        }


class OTPVerifySerializer(serializers.Serializer):
    """Verify OTP and get password"""

    vps_config_id = serializers.IntegerField()
    otp_code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        vps_config_id = attrs.get("vps_config_id")
        otp_code = attrs.get("otp_code")
        user = self.context["request"].user

        try:
            otp = OTPVerification.objects.get(
                user=user,
                vps_config_id=vps_config_id,
                otp_code=otp_code,
                is_used=False,
            )
        except OTPVerification.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP code.")

        if not otp.is_valid():
            raise serializers.ValidationError("OTP has expired or been used.")

        attrs["otp"] = otp
        return attrs

    def create(self, validated_data):
        otp = validated_data["otp"]
        vps_config = otp.vps_config
        
        # Mark OTP as used
        otp.is_used = True
        otp.used_at = timezone.now()
        otp.save()
        
        # Update access tracking
        vps_config.last_accessed_by = self.context["request"].user
        vps_config.last_accessed_at = timezone.now()
        vps_config.access_count += 1
        vps_config.save()
        
        # Decrypt password
        password = decrypt_password(vps_config.encrypted_password)
        
        return {
            "vps_config": vps_config,
            "password": password,
        }

    def to_representation(self, instance):
        return {
            "id": instance["vps_config"].id,
            "label": instance["vps_config"].label,
            "ip_address": instance["vps_config"].ip_address,
            "port": instance["vps_config"].port,
            "username": instance["vps_config"].username,
            "password": instance["password"],
            "message": "Password retrieved successfully. This will only be shown once.",
        }
