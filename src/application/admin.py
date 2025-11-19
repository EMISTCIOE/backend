"""
Application Admin
"""

from django.contrib import admin

from .models import EmailRequest


@admin.register(EmailRequest)
class EmailRequestAdmin(admin.ModelAdmin):
    list_display = [
        "subject",
        "requester_name",
        "request_type",
        "status",
        "requires_application",
        "request_number",
        "created_at",
    ]
    list_filter = ["request_type", "status", "requires_application", "created_at"]
    search_fields = [
        "subject",
        "requester_name",
        "requester_email",
        "message",
        "requested_email",
    ]
    readonly_fields = [
        "processed_at",
        "request_number",
        "created_at",
        "updated_at",
    ]
    
    fieldsets = (
        (
            "Requester Information",
            {
                "fields": (
                    "user",
                    "requester_name",
                    "requester_email",
                    "requester_phone",
                ),
            },
        ),
        (
            "Request Details",
            {
                "fields": (
                    "request_type",
                    "subject",
                    "message",
                    "requested_email",
                    "request_number",
                ),
            },
        ),
        (
            "Application",
            {
                "fields": (
                    "requires_application",
                    "application_document",
                ),
            },
        ),
        (
            "Status & Response",
            {
                "fields": (
                    "status",
                    "response_message",
                    "processed_by",
                    "processed_at",
                ),
            },
        ),
    )
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        # Make requires_application readonly after creation
        if obj and obj.pk:
            readonly.append("requires_application")
        return readonly
