"""
EMIS Admin registration for VPS info, hardware, and email reset requests.
"""

from django.contrib import admin

from .models import EMISHardware, EMISVPSInfo, EMISVPSService, EmailResetRequest


@admin.register(EMISVPSInfo)
class EMISVPSInfoAdmin(admin.ModelAdmin):
    list_display = ["vps_name", "ip_address", "ram_gb", "cpu_cores", "is_active", "created_at"]
    search_fields = ["vps_name", "ip_address"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("vps_name", "ip_address", "ram_gb", "cpu_cores", "storage_gb")}),
        ("Details", {"fields": ("description", "notes")}),
        ("Status", {"fields": ("is_active",)}),
    )


@admin.register(EMISVPSService)
class EMISVPSServiceAdmin(admin.ModelAdmin):
    list_display = ["name", "vps", "port", "domain", "service_type", "is_active"]
    list_filter = ["vps", "is_active", "is_ssl_enabled"]
    search_fields = ["name", "domain", "service_type"]
    readonly_fields = ["url", "created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("vps", "name", "port", "service_type", "domain")}),
        ("SSL", {"fields": ("is_ssl_enabled",)}),
        ("Details", {"fields": ("description", "url")}),
        ("Status", {"fields": ("is_active",)}),
    )


@admin.register(EMISHardware)
class EMISHardwareAdmin(admin.ModelAdmin):
    list_display = ["name", "hardware_type", "ip_address", "location", "is_active"]
    list_filter = ["hardware_type", "is_active"]
    search_fields = ["name", "location"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("name", "hardware_type", "ip_address", "location")}),
        ("Media", {"fields": ("thumbnail_image",)}),
        ("Technical", {"fields": ("endpoints", "specifications")}),
        ("Details", {"fields": ("description",)}),
        ("Status", {"fields": ("is_active",)}),
    )


@admin.register(EmailResetRequest)
class EmailResetRequestAdmin(admin.ModelAdmin):
    list_display = ["roll_number", "full_name", "status", "phone_number", "request_sequence", "created_at"]
    list_filter = ["status", "request_sequence"]
    search_fields = ["roll_number", "full_name", "primary_email", "phone_number"]
    readonly_fields = ["request_sequence", "created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("full_name", "roll_number", "birth_date", "phone_number")}),
        ("Email", {"fields": ("primary_email", "secondary_email")}),
        ("Status", {"fields": ("status", "processed_at", "processed_by", "notes")}),
        ("System", {"fields": ("request_sequence", "created_at", "updated_at")}),
    )
