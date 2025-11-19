"""
EMIS Management data models
"""

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from src.base.models import AuditInfoModel


ROLL_NUMBER_PATTERN = r"^[A-Z]{3}\d{3}[A-Z]{3}\d{3}$"
PRIMARY_EMAIL_DOMAIN = "@tcio.edu.np"


class HardwareType(models.TextChoices):
    ROUTER = "router", _("Router")
    SWITCH = "switch", _("Switch")
    SERVER = "server", _("Server")
    FIREWALL = "firewall", _("Firewall")
    ENDPOINT = "endpoint", _("Endpoint")
    OTHER = "other", _("Other")


class EMISVPSInfo(AuditInfoModel):
    """
    Single VPS entry used by SMIA to describe EMIS services.
    """

    vps_label = models.CharField(
        _("VPS label"),
        max_length=255,
        unique=True,
        help_text=_("Friendly name for this VPS"),
    )
    ip_address = models.GenericIPAddressField(_("IP address"))
    description = models.TextField(_("description"), blank=True)
    notes = models.TextField(_("notes"), blank=True)
    affiliated_ports = models.JSONField(
        _("affiliated ports"),
        default=list,
        blank=True,
        help_text=_(
            "List of ports with service metadata, e.g. "
            "[{'port': 22, 'service': 'SSH', 'label': 'Remote Admin'}]",
        ),
    )

    class Meta:
        verbose_name = _("EMIS VPS information")
        verbose_name_plural = _("EMIS VPS information")
        ordering = ["vps_label"]

    def __str__(self):
        return self.vps_label

    def get_affiliated_ports(self):
        return self.affiliated_ports or []


class EMISHardware(AuditInfoModel):
    """
    Hardware inventory (routers, servers, endpoints) for EMIS.
    """

    name = models.CharField(_("name"), max_length=255)
    hardware_type = models.CharField(
        _("hardware type"),
        max_length=32,
        choices=HardwareType.choices,
        default=HardwareType.SERVER,
    )
    ip_address = models.GenericIPAddressField(_("IP address"), null=True, blank=True)
    location = models.CharField(_("location"), max_length=255, blank=True)
    endpoints = models.JSONField(
        _("endpoints"),
        default=list,
        blank=True,
        help_text=_("List of URLs, ports or services this device exposes."),
    )
    description = models.TextField(_("description"), blank=True)

    class Meta:
        verbose_name = _("EMIS hardware")
        verbose_name_plural = _("EMIS hardware")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.hardware_type})"


class EmailResetRequest(AuditInfoModel):
    """
    Tracks user-submitted email reset requests with roll validation and limits.
    """

    full_name = models.CharField(_("full name"), max_length=255)
    roll_number = models.CharField(
        _("roll number"),
        max_length=12,
        validators=[
            RegexValidator(
                regex=ROLL_NUMBER_PATTERN,
                message=_("Roll number must follow pattern THA080BCT002."),
            ),
        ],
        help_text=_("Format example: THA080BCT002"),
    )
    birth_date = models.DateField(_("birth date"))
    primary_email = models.EmailField(_("primary email"))
    secondary_email = models.EmailField(_("secondary email"))
    request_sequence = models.PositiveSmallIntegerField(
        _("request sequence"),
        default=1,
        editable=False,
        help_text=_("The number of reset attempts already recorded for this roll."),
    )

    class Meta:
        verbose_name = _("email reset request")
        verbose_name_plural = _("email reset requests")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.roll_number} · {self.full_name}"

    def save(self, *args, **kwargs):
        if not self.request_sequence:
            existing = EmailResetRequest.objects.filter(
                roll_number__iexact=self.roll_number,
            ).count()
            self.request_sequence = existing + 1
        super().save(*args, **kwargs)

    @property
    def requests_remaining(self):
        return max(0, 10 - self.request_sequence)
