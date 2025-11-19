"""
EMIS Admin
"""

from django.contrib import admin

from .models import OTPVerification, VPSConfiguration


@admin.register(VPSConfiguration)
class VPSConfigurationAdmin(admin.ModelAdmin):
    list_display = [
        "label",
        "ip_address",
        "port",
        "access_count",
        "is_active",
    ]
    list_filter = ["is_active"]
    search_fields = ["label", "ip_address", "username"]
    readonly_fields = [
        "encrypted_password",
        "last_accessed_at",
        "last_accessed_by",
        "access_count",
    ]
    fieldsets = (
        (
            "VPS Information",
            {
                "fields": ("label", "ip_address", "port", "description"),
            },
        ),
        (
            "Credentials",
            {
                "fields": ("username", "encrypted_password"),
            },
        ),
        (
            "Services",
            {
                "fields": ("services", "notes"),
            },
        ),
        (
            "Access Tracking",
            {
                "fields": (
                    "last_accessed_by",
                    "last_accessed_at",
                    "access_count",
                ),
            },
        ),
        (
            "Status",
            {
                "fields": ("is_active",),
            },
        ),
    )


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "vps_config",
        "otp_code",
        "is_used",
        "created_at",
        "expires_at",
    ]
    list_filter = ["is_used"]
    search_fields = ["user__email", "vps_config__label"]
    readonly_fields = ["created_at", "used_at"]
