"""
Meeting Enquiry Models
Centralized meeting request system with email templates
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from src.base.models import AuditInfoModel


class MeetingEnquiry(AuditInfoModel):
    """
    Meeting/Enquiry Request Model
    - Any student/public can request meeting with admins
    - Email notification system
    - Response tracking with custom email templates
    """

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("REJECTED", "Rejected"),
        ("COMPLETED", "Completed"),
    ]

    # Requester info
    requester_name = models.CharField(_("requester name"), max_length=255)
    requester_email = models.EmailField(_("requester email"))
    requester_phone = models.CharField(
        _("requester phone"),
        max_length=15,
        blank=True,
    )
    requester_student_id = models.CharField(
        _("student ID"),
        max_length=50,
        blank=True,
        help_text="Optional student ID if requester is a student",
    )
    
    # Meeting details
    requested_admin = models.ForeignKey(
        "user.User",
        on_delete=models.PROTECT,
        related_name="meeting_requests",
        help_text="Admin to meet with (Campus Chief, Assistant, HOD, DHOD)",
    )
    subject = models.CharField(_("subject"), max_length=255)
    message = models.TextField(_("message"))
    preferred_date = models.DateField(
        _("preferred date"),
        null=True,
        blank=True,
    )
    preferred_time = models.TimeField(
        _("preferred time"),
        null=True,
        blank=True,
    )
    
    # Response
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
    )
    response_message = models.TextField(
        _("response message"),
        blank=True,
    )
    responded_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="responded_enquiries",
    )
    responded_at = models.DateTimeField(
        _("responded at"),
        null=True,
        blank=True,
    )
    
    # Meeting schedule (if accepted)
    scheduled_date = models.DateField(
        _("scheduled date"),
        null=True,
        blank=True,
    )
    scheduled_time = models.TimeField(
        _("scheduled time"),
        null=True,
        blank=True,
    )
    meeting_location = models.CharField(
        _("meeting location"),
        max_length=255,
        blank=True,
    )
    meeting_notes = models.TextField(
        _("meeting notes"),
        blank=True,
        help_text="Internal notes about the meeting",
    )
    
    # Email tracking
    email_sent = models.BooleanField(
        _("email sent"),
        default=False,
    )
    email_sent_at = models.DateTimeField(
        _("email sent at"),
        null=True,
        blank=True,
    )
    
    class Meta:
        verbose_name = _("meeting enquiry")
        verbose_name_plural = _("meeting enquiries")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["requested_admin", "status"]),
            models.Index(fields=["requester_email"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.subject} - {self.requester_name}"

    def get_admin_role(self):
        """Get the role of the requested admin"""
        if hasattr(self.requested_admin, 'admin_profiles'):
            profile = self.requested_admin.admin_profiles.filter(
                is_active=True,
            ).first()
            if profile:
                return profile.get_role_type_display()
        return "Admin"
