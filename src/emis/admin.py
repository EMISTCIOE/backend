"""
EMIS Admin registration for VPS info, hardware, and email reset requests.
"""

from django.contrib import admin

from .models import EMISHardware, EMISVPSInfo, EmailResetRequest


@admin.register(EMISVPSInfo)
class EMISVPSInfoAdmin(admin.ModelAdmin):
    list_display = ["vps_label", "ip_address", "is_active", "created_at"]
    search_fields = ["vps_label", "ip_address"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("vps_label", "ip_address", "description", "notes")}),
        ("Affiliated ports", {"fields": ("affiliated_ports",)}),
        ("Status", {"fields": ("is_active",)}),
    )


@admin.register(EMISHardware)
class EMISHardwareAdmin(admin.ModelAdmin):
    list_display = ["name", "hardware_type", "ip_address", "is_active"]
    list_filter = ["hardware_type", "is_active"]
    search_fields = ["name", "location"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("name", "hardware_type", "ip_address", "location", "description")}),
        ("Endpoints", {"fields": ("endpoints",)}),
        ("Status", {"fields": ("is_active",)}),
    )


@admin.register(EmailResetRequest)
class EmailResetRequestAdmin(admin.ModelAdmin):
    list_display = ["roll_number", "full_name", "request_sequence", "primary_email", "created_at"]
    list_filter = ["request_sequence"]
    search_fields = ["roll_number", "full_name", "primary_email"]
    readonly_fields = ["request_sequence", "created_at", "updated_at"]
    fields = (
        "full_name",
        "roll_number",
        "birth_date",
        "primary_email",
        "secondary_email",
        "request_sequence",
        "created_at",
        "updated_at",
    )
