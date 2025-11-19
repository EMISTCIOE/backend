"""
Email Request Models
Email requests with 10-request limit and application requirement
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from src.base.models import AuditInfoModel


class EmailRequest(AuditInfoModel):
    """
    Email Request Model
    - Track email requests per user
    - Max 10 requests without application
    - After 10 requests, application document required
    """

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("COMPLETED", "Completed"),
    ]

    REQUEST_TYPE_CHOICES = [
        ("NEW_EMAIL", "New Email Account"),
        ("PASSWORD_RESET", "Password Reset"),
        ("QUOTA_INCREASE", "Quota Increase"),
        ("FORWARDING", "Email Forwarding"),
        ("ALIAS", "Email Alias"),
        ("OTHER", "Other"),
    ]

    # Requester (can be user or external)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_requests",
        null=True,
        blank=True,
        help_text="Registered user (optional)",
    )
    requester_email = models.EmailField(_("requester email"))
    requester_name = models.CharField(_("requester name"), max_length=255)
    requester_phone = models.CharField(
        _("requester phone"),
        max_length=15,
        blank=True,
    )
    requester_department = models.CharField(
        _("department/affiliation"),
        max_length=255,
        blank=True,
    )
    
    # Request details
    request_type = models.CharField(
        _("request type"),
        max_length=20,
        choices=REQUEST_TYPE_CHOICES,
    )
    subject = models.CharField(_("subject"), max_length=255)
    message = models.TextField(_("message"))
    requested_email = models.EmailField(
        _("requested email"),
        blank=True,
        help_text="Email address being requested (for new account requests)",
    )
    
    # Application (required after 10 requests)
    requires_application = models.BooleanField(
        _("requires application"),
        default=False,
        help_text="Set to True if requester has 10+ requests",
    )
    application_document = models.FileField(
        _("application document"),
        upload_to="email_requests/applications/%Y/%m/",
        null=True,
        blank=True,
    )
    request_number = models.PositiveIntegerField(
        _("request number"),
        default=1,
        help_text="Number of requests from this user/email",
    )
    
    # Status
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
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_email_requests",
    )
    processed_at = models.DateTimeField(
        _("processed at"),
        null=True,
        blank=True,
    )
    
    # Email details (if approved)
    created_email = models.EmailField(
        _("created email"),
        blank=True,
        help_text="The actual email address that was created",
    )
    email_password = models.CharField(
        _("temporary password"),
        max_length=255,
        blank=True,
        help_text="Temporary password (if applicable)",
    )
    
    class Meta:
        verbose_name = _("email request")
        verbose_name_plural = _("email requests")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["requester_email", "status"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.subject} - {self.requester_name}"

    @staticmethod
    def get_user_request_count(user=None, email=None):
        """Get total request count for a user or email"""
        if user:
            return EmailRequest.objects.filter(user=user).count()
        elif email:
            return EmailRequest.objects.filter(requester_email=email).count()
        return 0

    @staticmethod
    def needs_application(user=None, email=None):
        """Check if user/email needs to submit application (10+ requests)"""
        count = EmailRequest.get_user_request_count(user, email)
        return count >= 10

    def save(self, *args, **kwargs):
        # Auto-calculate request number
        if not self.pk:  # New request
            if self.user:
                self.request_number = EmailRequest.get_user_request_count(
                    user=self.user,
                ) + 1
            else:
                self.request_number = EmailRequest.get_user_request_count(
                    email=self.requester_email,
                ) + 1
            
            # Check if application is required
            if self.request_number > 10 and not self.application_document:
                self.requires_application = True
        
        super().save(*args, **kwargs)
