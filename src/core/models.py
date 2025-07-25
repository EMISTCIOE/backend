from django.db import models
from django.utils.translation import gettext_lazy as _

from src.base.models import AuditInfoModel
from src.core.constants import EmailTypes


class FiscalSessionBS(AuditInfoModel):
    """
    Represents a fiscal session in Bikram Sambat (BS),
    used across campus reports and other resources.
    E.g., session_full: "2079/2080", session_short: "079/80"
    """

    session_full = models.CharField(
        _("Full Session"),
        max_length=9,
        unique=True,
        help_text=_("E.g. 2079/2080"),
    )
    session_short = models.CharField(
        _("Short Session"),
        max_length=5,
        unique=True,
        help_text=_("E.g. 79/80"),
    )

    class Meta:
        verbose_name = _("Fiscal Session (BS)")
        verbose_name_plural = _("Fiscal Sessions (BS)")

    def __str__(self):
        return self.session_short


class EmailConfig(AuditInfoModel):
    """Model to store email configuration settings."""

    email_type = models.CharField(
        choices=EmailTypes.choices(),
        max_length=20,
        unique=True,
        default="INFO",
        help_text="Type of email (e.g. sales, info)",
    )
    email_host = models.CharField(
        max_length=255,
        default="smtp.gmail.com",
        help_text="SMTP server address",
    )
    email_use_tls = models.BooleanField(
        default=True,
        help_text="Use TLS for the email connection",
    )
    email_use_ssl = models.BooleanField(
        default=False,
        help_text="Use SSL for the email connection",
    )
    email_port = models.PositiveIntegerField(
        default=587,
        help_text="Port for the email server",
    )
    email_host_user = models.EmailField(help_text="Email host user")
    email_host_password = models.CharField(
        max_length=255,
        help_text="Email host password",
    )
    default_from_email = models.EmailField(help_text="Default 'from' email address")
    server_mail = models.EmailField(
        blank=True,
        help_text="Email address for server errors",
    )

    def __str__(self):
        return f"EmailConfig (ID: {self.id}) - {self.email_type}"

    class Meta:
        verbose_name = _("Email Configuration")
        verbose_name_plural = _("Email Configurations")
