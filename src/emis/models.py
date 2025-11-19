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
    VPS server information with resource specifications and service management.
    """

    vps_name = models.CharField(
        _("VPS name"),
        max_length=255,
        unique=True,
        help_text=_("Name of the VPS server"),
    )
    ip_address = models.GenericIPAddressField(_("IP address"))
    ram_gb = models.PositiveIntegerField(
        _("RAM (GB)"),
        default=1,
        help_text=_("Total RAM in gigabytes"),
    )
    cpu_cores = models.PositiveIntegerField(
        _("CPU cores"),
        default=1,
        help_text=_("Number of CPU cores"),
    )
    storage_gb = models.PositiveIntegerField(
        _("Storage (GB)"),
        null=True,
        blank=True,
        help_text=_("Total storage in gigabytes"),
    )
    description = models.TextField(_("description"), blank=True)
    notes = models.TextField(_("notes"), blank=True)

    class Meta:
        verbose_name = _("EMIS VPS information")
        verbose_name_plural = _("EMIS VPS information")
        ordering = ["vps_name"]

    def __str__(self):
        return self.vps_name

    def get_services(self):
        return self.services.filter(is_active=True)


class EMISVPSService(AuditInfoModel):
    """
    Services running on VPS servers with port and domain information.
    """

    vps = models.ForeignKey(
        EMISVPSInfo,
        on_delete=models.CASCADE,
        related_name="services",
        verbose_name=_("VPS server"),
    )
    name = models.CharField(
        _("service name"),
        max_length=255,
        help_text=_("Name of the service (e.g., ecast, portal)"),
    )
    port = models.PositiveIntegerField(
        _("port"),
        help_text=_("Port number the service runs on"),
    )
    service_type = models.CharField(
        _("service type"),
        max_length=100,
        help_text=_("Type of service (e.g., ecast.service, nginx.service)"),
    )
    domain = models.CharField(
        _("domain"),
        max_length=255,
        help_text=_("Domain name for the service (e.g., ecast.tcioe.edu.np)"),
    )
    is_ssl_enabled = models.BooleanField(
        _("SSL enabled"),
        default=False,
        help_text=_("Whether SSL/TLS is enabled for this service"),
    )
    description = models.TextField(_("description"), blank=True)

    class Meta:
        verbose_name = _("VPS service")
        verbose_name_plural = _("VPS services")
        unique_together = [["vps", "port"], ["vps", "name"]]
        ordering = ["vps", "port"]

    def __str__(self):
        return f"{self.vps.vps_name} - {self.name}:{self.port}"

    @property
    def url(self):
        protocol = "https" if self.is_ssl_enabled else "http"
        port_suffix = f":{self.port}" if self.port not in [80, 443] else ""
        return f"{protocol}://{self.domain}{port_suffix}"


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
    thumbnail_image = models.ImageField(
        _("thumbnail image"),
        upload_to="emis/hardware/thumbnails/",
        null=True,
        blank=True,
        help_text=_("Thumbnail image of the hardware device"),
    )
    endpoints = models.JSONField(
        _("endpoints"),
        default=list,
        blank=True,
        help_text=_("List of URLs, ports or services this device exposes."),
    )
    description = models.TextField(_("description"), blank=True)
    specifications = models.JSONField(
        _("specifications"),
        default=dict,
        blank=True,
        help_text=_("Hardware specifications like RAM, CPU, storage, etc."),
    )

    class Meta:
        verbose_name = _("EMIS hardware")
        verbose_name_plural = _("EMIS hardware")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.hardware_type})"


class RequestStatus(models.TextChoices):
    PENDING = "pending", _("Pending")
    APPROVED = "approved", _("Approved")
    REJECTED = "rejected", _("Rejected")


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
    phone_number = models.CharField(
        _("phone number"),
        max_length=20,
        default="9800000000",
        help_text=_("Contact phone number for verification"),
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=RequestStatus.choices,
        default=RequestStatus.PENDING,
        help_text=_("Current status of the reset request"),
    )
    request_sequence = models.PositiveSmallIntegerField(
        _("request sequence"),
        default=1,
        editable=False,
        help_text=_("The number of reset attempts already recorded for this roll."),
    )
    processed_at = models.DateTimeField(
        _("processed at"),
        null=True,
        blank=True,
        help_text=_("When the request was approved or rejected"),
    )
    processed_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_reset_requests",
        verbose_name=_("processed by"),
        help_text=_("Staff member who approved or rejected this request"),
    )
    notes = models.TextField(
        _("processing notes"),
        blank=True,
        help_text=_("Additional notes from the processing staff member"),
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
