"""
EMIS Admin registration for VPS info, hardware, and email reset requests.
"""

from django.contrib import admin

from .models import EMISHardware, EMISVPSInfo, EMISVPSService, EmailResetRequest


@admin.register(EMISVPSInfo)
class EMISVPSInfoAdmin(admin.ModelAdmin):
    list_display = [
        "vps_name",
        "environment",
        "provider",
        "ip_address",
        "ram_gb",
        "cpu_cores",
        "health_status",
        "status",
        "is_active",
    ]
    list_filter = ["environment", "provider", "health_status", "status", "is_active"]
    search_fields = ["vps_name", "slug", "ip_address", "private_ip_address", "tags"]
    readonly_fields = ["slug", "created_at", "updated_at", "last_health_check_at"]
    fieldsets = (
        ("Identity", {"fields": ("vps_name", "slug", "provider", "environment", "status", "health_status")}),
        ("Networking", {"fields": ("ip_address", "private_ip_address", "location", "ssh_port")}),
        ("Resources", {"fields": ("ram_gb", "cpu_cores", "storage_gb", "storage_type", "bandwidth_tb")}),
        ("Software", {"fields": ("operating_system", "kernel_version", "monitoring_url", "last_health_check_at")}),
        ("Tags", {"fields": ("tags",)}),
        ("Details", {"fields": ("description", "notes", "is_active")}),
        ("Audit", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(EMISVPSService)
class EMISVPSServiceAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "service_key",
        "vps",
        "protocol",
        "port",
        "domain",
        "status",
        "is_active",
    ]
    list_filter = ["vps", "status", "protocol", "is_ssl_enabled", "deploy_strategy"]
    search_fields = ["name", "service_key", "domain", "maintained_by"]
    readonly_fields = ["url", "created_at", "updated_at", "last_deployed_at"]
    fieldsets = (
        ("Identity", {"fields": ("vps", "name", "service_key", "maintained_by", "status")}),
        ("Networking", {"fields": ("protocol", "port", "domain", "is_ssl_enabled")}),
        ("Ops", {"fields": ("service_type", "deploy_strategy", "auto_restart", "version", "last_deployed_at")}),
        ("Health", {"fields": ("healthcheck_endpoint", "healthcheck_expectation", "url")}),
        ("Meta", {"fields": ("description", "metadata", "is_active")}),
        ("Audit", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(EMISHardware)
class EMISHardwareAdmin(admin.ModelAdmin):
    list_display = [
        "asset_tag",
        "name",
        "hardware_type",
        "environment",
        "status",
        "location",
        "ip_address",
        "is_active",
    ]
    list_filter = ["hardware_type", "environment", "status", "is_active"]
    search_fields = ["asset_tag", "name", "location", "ip_address", "responsible_team"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        ("Identity", {"fields": ("asset_tag", "name", "hardware_type", "status", "environment")}),
        ("Vendor", {"fields": ("manufacturer", "model_number", "serial_number", "responsible_team")}),
        ("Location", {"fields": ("location", "rack_unit", "ip_address")}),
        ("Lifecycle", {"fields": ("purchase_date", "warranty_expires_at", "power_draw_watts")}),
        ("Media", {"fields": ("thumbnail_image",)}),
        ("Technical", {"fields": ("endpoints", "specifications", "metadata")}),
        ("Details", {"fields": ("description", "is_active")}),
        ("Audit", {"fields": ("created_at", "updated_at")}),
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
