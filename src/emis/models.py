"""EMIS Management data models"""

import uuid

from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from src.base.models import AuditInfoModel


ROLL_NUMBER_PATTERN = r"^[A-Z]{3}\d{3}[A-Z]{3}\d{3}$"
PRIMARY_EMAIL_DOMAIN = "@tcioe.edu.np"


class HardwareType(models.TextChoices):
    # Network Equipment
    ROUTER = "router", _("Router")
    SWITCH = "switch", _("Switch")
    FIREWALL = "firewall", _("Firewall")
    ACCESS_POINT = "access_point", _("Access Point")
    MODEM = "modem", _("Modem")
    REPEATER = "repeater", _("Repeater")
    BRIDGE = "bridge", _("Bridge")
    GATEWAY = "gateway", _("Gateway")
    LOAD_BALANCER = "load_balancer", _("Load Balancer")
    
    # Computing Equipment  
    SERVER = "server", _("Server")
    DESKTOP = "desktop", _("Desktop Computer")
    LAPTOP = "laptop", _("Laptop")
    TABLET = "tablet", _("Tablet")
    MOBILE = "mobile", _("Mobile Device")
    
    # Storage Equipment
    STORAGE = "storage", _("Storage Array")
    NAS = "nas", _("Network Attached Storage")
    SAN = "san", _("Storage Area Network")
    
    # Peripherals
    PRINTER = "printer", _("Printer")
    SCANNER = "scanner", _("Scanner")
    MONITOR = "monitor", _("Monitor")
    PROJECTOR = "projector", _("Projector")
    CAMERA = "camera", _("Camera")
    
    # Communication
    TELEPHONE = "telephone", _("Telephone")
    
    # Infrastructure
    UPS = "ups", _("UPS / Power")
    PDU = "pdu", _("Power Distribution Unit")
    RACK = "rack", _("Server Rack")
    KVM = "kvm", _("KVM Switch")
    ENDPOINT = "endpoint", _("Endpoint")
    
    OTHER = "other", _("Other")


class EnvironmentType(models.TextChoices):
    PRODUCTION = "production", _("Production")
    STAGING = "staging", _("Staging")
    DEVELOPMENT = "development", _("Development")
    LAB = "lab", _("Lab / Prototype")


class ProviderType(models.TextChoices):
    DIGITALOCEAN = "digitalocean", _("DigitalOcean")
    LIGHTSAIL = "lightsail", _("AWS Lightsail")
    HETZNER = "hetzner", _("Hetzner")
    ON_PREM = "on-prem", _("On-premises / Bare Metal")
    OTHER = "other", _("Other")


class NodeStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    MAINTENANCE = "maintenance", _("Maintenance")
    RETIRED = "retired", _("Retired")
    DECOMMISSIONED = "decommissioned", _("Decommissioned")


class HealthStatus(models.TextChoices):
    HEALTHY = "healthy", _("Healthy")
    DEGRADED = "degraded", _("Degraded")
    OUTAGE = "outage", _("Outage")
    UNKNOWN = "unknown", _("Unknown")


class ServiceStatus(models.TextChoices):
    RUNNING = "running", _("Running")
    PAUSED = "paused", _("Paused")
    FAILED = "failed", _("Failed")
    DEPLOYING = "deploying", _("Deploying")


class ServiceProtocol(models.TextChoices):
    HTTP = "http", _("HTTP")
    HTTPS = "https", _("HTTPS")
    TCP = "tcp", _("TCP")
    UDP = "udp", _("UDP")


class DeployStrategy(models.TextChoices):
    MANUAL = "manual", _("Manual")
    GITOPS = "gitops", _("GitOps")
    CI_CD = "ci_cd", _("CI / CD")


class DownloadCategory(models.TextChoices):
    REPORTS = "reports", _("Reports")
    FORMS = "forms", _("Forms")
    DOWNLOADS = "downloads", _("Downloads")


class NoticeCategory(models.TextChoices):
    SECURITY = "security", _("Security Update")
    MAINTENANCE = "maintenance", _("Maintenance")
    RELEASE = "release", _("Release & Feature")
    ADVISORY = "advisory", _("Advisory")
    GENERAL = "general", _("General")


class NoticeSeverity(models.TextChoices):
    INFO = "info", _("Info")
    MINOR = "minor", _("Minor")
    MAJOR = "major", _("Major")
    CRITICAL = "critical", _("Critical")


class HardwareStatus(models.TextChoices):
    OPERATIONAL = "operational", _("Operational")
    STANDBY = "standby", _("Standby")
    MAINTENANCE = "maintenance", _("Maintenance")
    RETIRED = "retired", _("Retired")


def _generate_unique_slug(model, base_value: str, fallback: str = "item") -> str:
    """Generate a unique slug for the provided model using the base value."""
    base_slug = slugify(base_value) or fallback
    slug_candidate = base_slug
    suffix = 1
    while model.objects.filter(slug=slug_candidate).exists():
        slug_candidate = f"{base_slug}-{suffix}"
        suffix += 1
    return slug_candidate


class EMISDownload(AuditInfoModel):
    """Downloadable assets specifically for EMIS (reports/forms vs resources)."""

    title = models.CharField(_("Title"), max_length=150)
    description = models.TextField(_("Description"), blank=True)
    category = models.CharField(
        _("Category"),
        max_length=20,
        choices=DownloadCategory.choices,
        default=DownloadCategory.DOWNLOADS,
    )
    file = models.FileField(
        _("File"),
        upload_to="emis/downloads/",
        null=True,
        blank=True,
        help_text=_("Upload the downloadable document or form."),
    )
    link_url = models.URLField(
        _("Link URL"),
        blank=True,
        help_text=_("Optional external link if the file is hosted elsewhere."),
    )

    class Meta:
        verbose_name = _("EMIS download")
        verbose_name_plural = _("EMIS downloads")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def clean(self):
        """Ensure at least one of file/link_url is provided."""
        if not self.file and not self.link_url:
            raise ValidationError(_("Either a file or a link URL must be provided."))
        super().clean()


class EMISNotice(AuditInfoModel):
    """Operational and security notices specific to the EMIS platform."""

    slug = models.SlugField(_("Slug"), max_length=255, unique=True, blank=True)
    title = models.CharField(_("Title"), max_length=200)
    summary = models.CharField(_("Summary"), max_length=300, blank=True)
    body = RichTextField(_("Body"), blank=True)
    category = models.CharField(
        _("Category"),
        max_length=20,
        choices=NoticeCategory.choices,
        default=NoticeCategory.GENERAL,
    )
    severity = models.CharField(
        _("Severity"),
        max_length=20,
        choices=NoticeSeverity.choices,
        default=NoticeSeverity.INFO,
    )
    published_at = models.DateTimeField(_("Published at"), default=timezone.now)
    is_published = models.BooleanField(
        _("Published"),
        default=True,
        help_text=_("Unpublish to hide the notice from the public feed."),
    )
    attachment = models.FileField(
        _("Attachment"),
        upload_to="emis/notices/",
        null=True,
        blank=True,
        help_text=_("Optional attachment such as a PDF advisory."),
    )
    external_url = models.URLField(
        _("External URL"),
        blank=True,
        help_text=_("Optional reference link for more details."),
    )
    views = models.PositiveIntegerField(_("Views"), default=0)

    class Meta:
        verbose_name = _("EMIS notice")
        verbose_name_plural = _("EMIS notices")
        ordering = ["-published_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["category"]),
            models.Index(fields=["severity"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = _generate_unique_slug(EMISNotice, self.title, fallback="emis-notice")
        super().save(*args, **kwargs)

    def increment_views(self):
        EMISNotice.objects.filter(pk=self.pk).update(views=models.F("views") + 1)
        self.refresh_from_db(fields=["views"])


class EMISVPSInfo(AuditInfoModel):
    """VPS server information with resource specifications and operational metadata."""

    vps_name = models.CharField(
        _("VPS name"),
        max_length=255,
        unique=True,
        help_text=_("Human friendly name of the virtual server"),
    )
    slug = models.SlugField(
        _("slug"),
        unique=True,
        blank=True,
        help_text=_("Stable identifier used by automation and IaC"),
    )
    provider = models.CharField(
        _("provider"),
        max_length=50,
        choices=ProviderType.choices,
        default=ProviderType.DIGITALOCEAN,
    )
    environment = models.CharField(
        _("environment"),
        max_length=32,
        choices=EnvironmentType.choices,
        default=EnvironmentType.PRODUCTION,
    )
    status = models.CharField(
        _("status"),
        max_length=32,
        choices=NodeStatus.choices,
        default=NodeStatus.ACTIVE,
    )
    health_status = models.CharField(
        _("health status"),
        max_length=32,
        choices=HealthStatus.choices,
        default=HealthStatus.UNKNOWN,
    )
    ip_address = models.GenericIPAddressField(_("public IP address"))
    private_ip_address = models.GenericIPAddressField(
        _("private IP address"),
        null=True,
        blank=True,
    )
    location = models.CharField(
        _("location"),
        max_length=255,
        default="N/A",
        help_text=_("Datacenter region or rack name"),
    )
    ram_gb = models.PositiveIntegerField(
        _("RAM (GB)"),
        default=2,
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
    storage_type = models.CharField(
        _("storage type"),
        max_length=50,
        default="SSD",
        help_text=_("SSD, NVMe, HDD, etc."),
    )
    bandwidth_tb = models.DecimalField(
        _("bandwidth (TB)"),
        max_digits=5,
        decimal_places=2,
        default=1,
    )
    ssh_port = models.PositiveIntegerField(
        _("SSH port"),
        default=22,
        help_text=_("Port for secure shell access"),
    )
    operating_system = models.CharField(
        _("operating system"),
        max_length=120,
        default="Ubuntu 22.04 LTS",
    )
    kernel_version = models.CharField(
        _("kernel version"),
        max_length=120,
        blank=True,
    )
    monitoring_url = models.URLField(
        _("monitoring dashboard"),
        blank=True,
        help_text=_("Link to Grafana, Uptime Kuma or any monitoring panel"),
    )
    last_health_check_at = models.DateTimeField(
        _("last health check"),
        null=True,
        blank=True,
    )
    tags = models.JSONField(
        _("tags"),
        default=list,
        blank=True,
        help_text=_("Free-form labels used for grouping (team, stack, batch, etc.)"),
    )
    description = models.TextField(_("description"), blank=True)
    notes = models.TextField(_("notes"), blank=True)

    class Meta:
        verbose_name = _("EMIS VPS information")
        verbose_name_plural = _("EMIS VPS information")
        ordering = ["vps_name"]

    def __str__(self):
        return f"{self.vps_name} [{self.environment}]"

    def save(self, *args, **kwargs):
        base_slug = slugify(self.vps_name) or str(uuid.uuid4())
        slug_candidate = base_slug
        counter = 1
        while EMISVPSInfo.objects.exclude(pk=self.pk).filter(slug=slug_candidate).exists():
            slug_candidate = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug_candidate
        super().save(*args, **kwargs)

    def get_services(self):
        return self.services.filter(is_active=True)

    def mark_health(self, status: str, when=None):
        if status not in HealthStatus.values:
            raise ValueError("Invalid health status")
        self.health_status = status
        self.last_health_check_at = when or timezone.now()
        self.save(
            update_fields=[
                "health_status",
                "last_health_check_at",
                "updated_at",
                "updated_by",
            ]
        )


class EMISVPSService(AuditInfoModel):
    """Services running on VPS servers with deployment metadata and health info."""

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
    service_key = models.CharField(
        _("service key"),
        max_length=120,
        help_text=_("Systemd unit, container name or identifier"),
    )
    port = models.PositiveIntegerField(
        _("port"),
        help_text=_("Port number the service runs on"),
    )
    protocol = models.CharField(
        _("protocol"),
        max_length=10,
        choices=ServiceProtocol.choices,
        default=ServiceProtocol.HTTP,
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
    healthcheck_endpoint = models.CharField(
        _("healthcheck endpoint"),
        max_length=255,
        blank=True,
        help_text=_("Relative path or URL used for heartbeat checks"),
    )
    healthcheck_expectation = models.CharField(
        _("health expectation"),
        max_length=255,
        blank=True,
        help_text=_("Expected response (status code, JSON key, etc.)"),
    )
    version = models.CharField(
        _("version"),
        max_length=50,
        blank=True,
    )
    deploy_strategy = models.CharField(
        _("deploy strategy"),
        max_length=32,
        choices=DeployStrategy.choices,
        default=DeployStrategy.MANUAL,
    )
    auto_restart = models.BooleanField(
        _("auto restart"),
        default=True,
        help_text=_("Whether supervisors/systemd restart the service"),
    )
    maintained_by = models.CharField(
        _("maintained by"),
        max_length=255,
        blank=True,
        help_text=_("Owning team or point of contact"),
    )
    status = models.CharField(
        _("status"),
        max_length=32,
        choices=ServiceStatus.choices,
        default=ServiceStatus.RUNNING,
    )
    last_deployed_at = models.DateTimeField(
        _("last deployed at"),
        null=True,
        blank=True,
    )
    description = models.TextField(_("description"), blank=True)
    metadata = models.JSONField(
        _("metadata"),
        default=dict,
        blank=True,
        help_text=_("Free-form JSON for env vars, scaling hints, etc."),
    )

    class Meta:
        verbose_name = _("VPS service")
        verbose_name_plural = _("VPS services")
        unique_together = [["vps", "port"], ["vps", "name"], ["vps", "service_key"]]
        ordering = ["vps", "port"]

    def __str__(self):
        return f"{self.vps.vps_name} - {self.name}:{self.port}"

    @property
    def url(self):
        protocol = self.protocol if self.protocol in ["http", "https"] else "http"
        port_suffix = f":{self.port}" if self.port not in [80, 443] else ""
        return f"{protocol}://{self.domain}{port_suffix}"

    def is_external(self):
        return self.protocol in {ServiceProtocol.HTTP, ServiceProtocol.HTTPS}


class EMISHardware(AuditInfoModel):
    """Hardware inventory (routers, servers, endpoints) for EMIS."""

    name = models.CharField(_("name"), max_length=255)
    asset_tag = models.CharField(
        _("asset tag"),
        max_length=64,
        unique=True,
        default=uuid.uuid4,
        help_text=_("Unique inventory tag or barcode ID"),
    )
    hardware_type = models.CharField(
        _("hardware type"),
        max_length=32,
        choices=HardwareType.choices,
        default=HardwareType.SERVER,
    )
    manufacturer = models.CharField(_("manufacturer"), max_length=120, blank=True)
    model_number = models.CharField(_("model number"), max_length=120, blank=True)
    serial_number = models.CharField(_("serial number"), max_length=120, blank=True)
    ip_address = models.GenericIPAddressField(_("IP address"), null=True, blank=True)
    location = models.CharField(_("location"), max_length=255, blank=True)
    environment = models.CharField(
        _("environment"),
        max_length=32,
        choices=EnvironmentType.choices,
        default=EnvironmentType.PRODUCTION,
    )
    status = models.CharField(
        _("status"),
        max_length=32,
        choices=HardwareStatus.choices,
        default=HardwareStatus.OPERATIONAL,
    )
    responsible_team = models.CharField(_("responsible team"), max_length=120, blank=True)
    purchase_date = models.DateField(_("purchase date"), null=True, blank=True)
    warranty_expires_at = models.DateField(_("warranty expires at"), null=True, blank=True)
    power_draw_watts = models.PositiveIntegerField(_("power draw (W)"), null=True, blank=True)
    rack_unit = models.CharField(_("rack / unit"), max_length=50, blank=True)
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
    metadata = models.JSONField(
        _("metadata"),
        default=dict,
        blank=True,
        help_text=_("Any extra structured data (interfaces, notes, etc.)"),
    )

    class Meta:
        verbose_name = _("EMIS hardware")
        verbose_name_plural = _("EMIS hardware")
        ordering = ["name"]

    def __str__(self):
        return f"{self.asset_tag} · {self.name}"


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
