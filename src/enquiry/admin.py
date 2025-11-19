"""
Enquiry Admin
"""

from django.contrib import admin

from .models import MeetingEnquiry


@admin.register(MeetingEnquiry)
class MeetingEnquiryAdmin(admin.ModelAdmin):
    list_display = [
        "subject",
        "requester_name",
        "requested_admin",
        "status",
        "created_at",
    ]
    list_filter = ["status", "email_sent"]
    search_fields = ["subject", "requester_name", "requester_email"]
    readonly_fields = ["responded_at", "email_sent_at", "created_at", "updated_at"]
    fieldsets = (
        (
            "Requester Information",
            {
                "fields": (
                    "requester_name",
                    "requester_email",
                    "requester_phone",
                    "requester_student_id",
                ),
            },
        ),
        (
            "Meeting Request",
            {
                "fields": (
                    "requested_admin",
                    "subject",
                    "message",
                    "preferred_date",
                    "preferred_time",
                ),
            },
        ),
        (
            "Response",
            {
                "fields": (
                    "status",
                    "response_message",
                    "responded_by",
                    "responded_at",
                ),
            },
        ),
        (
            "Meeting Schedule",
            {
                "fields": (
                    "scheduled_date",
                    "scheduled_time",
                    "meeting_location",
                    "meeting_notes",
                ),
            },
        ),
        (
            "Email Tracking",
            {
                "fields": ("email_sent", "email_sent_at"),
            },
        ),
    )
