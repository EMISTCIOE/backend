from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

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
        help_text=_("E.g. 079/80"),
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


class DashboardStats(models.Model):
    """
    Model to cache dashboard statistics for performance optimization.
    Stats are calculated and stored periodically or on-demand.
    """
    
    # Timestamp
    calculated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("When these statistics were last calculated")
    )
    
    # User Statistics
    total_users = models.IntegerField(default=0, help_text=_("Total number of users"))
    active_users = models.IntegerField(default=0, help_text=_("Users active in last 30 days"))
    new_users_this_month = models.IntegerField(default=0, help_text=_("New users registered this month"))
    users_by_role = models.JSONField(default=dict, blank=True, help_text=_("User count grouped by role"))
    
    # Department Statistics
    total_departments = models.IntegerField(default=0, help_text=_("Total number of departments"))
    active_departments = models.IntegerField(default=0, help_text=_("Active departments"))
    
    # Notice Statistics
    total_notices = models.IntegerField(default=0, help_text=_("Total number of notices"))
    active_notices = models.IntegerField(default=0, help_text=_("Published notices"))
    draft_notices = models.IntegerField(default=0, help_text=_("Draft notices"))
    featured_notices = models.IntegerField(default=0, help_text=_("Featured notices"))
    notices_by_category = models.JSONField(default=dict, blank=True, help_text=_("Notice count by category"))
    recent_notices_count = models.IntegerField(default=0, help_text=_("Notices published in last 7 days"))
    
    # Project Statistics
    total_projects = models.IntegerField(default=0, help_text=_("Total number of projects"))
    projects_by_status = models.JSONField(default=dict, blank=True, help_text=_("Projects grouped by status"))
    projects_by_type = models.JSONField(default=dict, blank=True, help_text=_("Projects grouped by type"))
    projects_by_department = models.JSONField(default=dict, blank=True, help_text=_("Projects per department"))
    completed_projects_this_year = models.IntegerField(default=0, help_text=_("Projects completed this year"))
    
    # Research Statistics
    total_research = models.IntegerField(default=0, help_text=_("Total research papers"))
    research_by_status = models.JSONField(default=dict, blank=True, help_text=_("Research grouped by status"))
    research_by_type = models.JSONField(default=dict, blank=True, help_text=_("Research grouped by type"))
    published_research_this_year = models.IntegerField(default=0, help_text=_("Research published this year"))
    
    # Journal Statistics
    total_articles = models.IntegerField(default=0, help_text=_("Total journal articles"))
    total_authors = models.IntegerField(default=0, help_text=_("Total authors"))
    total_board_members = models.IntegerField(default=0, help_text=_("Total board members"))
    
    # Curriculum Statistics
    total_subjects = models.IntegerField(default=0, help_text=_("Total subjects"))
    total_routines = models.IntegerField(default=0, help_text=_("Total class routines"))
    total_suggestions = models.IntegerField(default=0, help_text=_("Total suggestions received"))
    
    # Feedback Statistics
    total_feedback_submissions = models.IntegerField(default=0, help_text=_("Total feedback submissions"))
    pending_feedback = models.IntegerField(default=0, help_text=_("Pending feedback"))
    
    # Graph Data - Time Series
    notices_trend = models.JSONField(
        default=list, 
        blank=True, 
        help_text=_("Notice count over last 6 months [{month: 'Jan', count: 10}, ...]")
    )
    users_growth = models.JSONField(
        default=list, 
        blank=True, 
        help_text=_("User registration trend over last 6 months")
    )
    research_publications_trend = models.JSONField(
        default=list, 
        blank=True, 
        help_text=_("Research publications over last 12 months")
    )
    
    class Meta:
        verbose_name = _("Dashboard Statistics")
        verbose_name_plural = _("Dashboard Statistics")
        ordering = ['-calculated_at']
    
    def __str__(self):
        return f"Dashboard Stats - {self.calculated_at.strftime('%Y-%m-%d %H:%M')}"
    
    @classmethod
    def get_latest(cls):
        """Get the most recent statistics record"""
        return cls.objects.first()
    
    @classmethod
    def is_cache_valid(cls, max_age_minutes=30):
        """Check if cached stats are still valid (less than max_age_minutes old)"""
        latest = cls.get_latest()
        if not latest:
            return False
        age = timezone.now() - latest.calculated_at
        return age.total_seconds() < (max_age_minutes * 60)
