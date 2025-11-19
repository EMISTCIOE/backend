"""
EMIS Models
VPS Configuration with encrypted password and OTP viewing
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from src.base.models import AuditInfoModel


class VPSConfiguration(AuditInfoModel):
    """
    VPS Configuration Model
    - Only accessible by EMIS Staff
    - Stores VPS details with encrypted passwords
    - OTP required to view passwords
    """

    label = models.CharField(
        _("label"),
        max_length=255,
        unique=True,
        help_text="Descriptive name for this VPS",
    )
    ip_address = models.GenericIPAddressField(_("IP address"))
    port = models.PositiveIntegerField(
        _("port"),
        default=22,
    )
    services = models.JSONField(
        _("services"),
        default=list,
        blank=True,
        help_text="List of services running on this VPS with ports",
    )
    
    # Credentials (encrypted)
    username = models.CharField(_("username"), max_length=255)
    encrypted_password = models.CharField(
        _("encrypted password"),
        max_length=500,
        help_text="Password encrypted with Fernet",
    )
    
    # Access tracking
    last_accessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accessed_vps",
    )
    last_accessed_at = models.DateTimeField(
        _("last accessed at"),
        null=True,
        blank=True,
    )
    access_count = models.PositiveIntegerField(
        _("access count"),
        default=0,
    )
    
    # Additional info
    description = models.TextField(_("description"), blank=True)
    notes = models.TextField(
        _("notes"),
        blank=True,
        help_text="Internal notes about this VPS",
    )
    
    class Meta:
        verbose_name = _("VPS configuration")
        verbose_name_plural = _("VPS configurations")
        ordering = ["label"]

    def __str__(self):
        return f"{self.label} ({self.ip_address}:{self.port})"

    def get_services_display(self):
        """Get formatted services list"""
        if not self.services:
            return []
        return self.services


class OTPVerification(AuditInfoModel):
    """
    OTP Verification for viewing VPS passwords
    - Generate OTP for EMIS staff
    - Verify OTP before showing password
    - Track OTP usage
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vps_otps",
    )
    vps_config = models.ForeignKey(
        VPSConfiguration,
        on_delete=models.CASCADE,
        related_name="otp_verifications",
    )
    otp_code = models.CharField(
        _("OTP code"),
        max_length=6,
    )
    is_used = models.BooleanField(
        _("is used"),
        default=False,
    )
    used_at = models.DateTimeField(
        _("used at"),
        null=True,
        blank=True,
    )
    expires_at = models.DateTimeField(
        _("expires at"),
        help_text="OTP expires after 5 minutes",
    )
    
    class Meta:
        verbose_name = _("OTP verification")
        verbose_name_plural = _("OTP verifications")
        ordering = ["-created_at"]

    def __str__(self):
        return f"OTP for {self.user.email} - {self.vps_config.label}"

    def is_valid(self):
        """Check if OTP is still valid"""
        from django.utils import timezone
        return not self.is_used and timezone.now() < self.expires_at
