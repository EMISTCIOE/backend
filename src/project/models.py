from django.db import models
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField

from src.base.models import AuditInfoModel
from src.department.models import Department


PROJECT_STATUS_CHOICES = [
    ('draft', _('Draft')),
    ('in_progress', _('In Progress')),
    ('completed', _('Completed')),
    ('cancelled', _('Cancelled')),
]

PROJECT_TYPE_CHOICES = [
    ('final_year', _('Final Year Project')),
    ('minor', _('Minor Project')),
    ('major', _('Major Project')),
    ('research', _('Research Project')),
    ('other', _('Other')),
]


class Project(AuditInfoModel):
    """
    Model for student projects
    """
    title = models.CharField(
        _("Project Title"),
        max_length=300,
        help_text=_("Title of the project")
    )
    
    description = RichTextField(
        _("Project Description"),
        help_text=_("Detailed description of the project"),
        blank=True
    )
    
    abstract = models.TextField(
        _("Abstract"),
        help_text=_("Brief abstract of the project"),
        blank=True
    )
    
    project_type = models.CharField(
        _("Project Type"),
        max_length=20,
        choices=PROJECT_TYPE_CHOICES,
        default='final_year'
    )
    
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=PROJECT_STATUS_CHOICES,
        default='draft'
    )
    
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Department"),
        help_text=_("Department (optional)")
    )
    
    supervisor_name = models.CharField(
        _("Supervisor Name"),
        max_length=200,
        help_text=_("Name of the project supervisor")
    )
    
    supervisor_email = models.EmailField(
        _("Supervisor Email"),
        blank=True,
        help_text=_("Email of the project supervisor")
    )
    
    start_date = models.DateField(
        _("Start Date"),
        null=True,
        blank=True
    )
    
    end_date = models.DateField(
        _("End Date"),
        null=True,
        blank=True
    )
    
    academic_year = models.CharField(
        _("Academic Year"),
        max_length=20,
        help_text=_("Academic year (e.g., 2024-2025)"),
        blank=True
    )
    
    github_url = models.URLField(
        _("GitHub URL"),
        blank=True,
        help_text=_("GitHub repository URL")
    )
    
    demo_url = models.URLField(
        _("Demo URL"),
        blank=True,
        help_text=_("Live demo URL")
    )
    
    report_file = models.FileField(
        _("Project Report"),
        upload_to='projects/reports/',
        blank=True,
        help_text=_("Upload project report PDF")
    )
    
    thumbnail = models.ImageField(
        _("Thumbnail"),
        upload_to='projects/thumbnails/',
        blank=True,
        help_text=_("Project thumbnail image")
    )
    
    technologies_used = models.TextField(
        _("Technologies Used"),
        blank=True,
        help_text=_("List of technologies/tools used (comma separated)")
    )
    
    is_featured = models.BooleanField(
        _("Featured Project"),
        default=False,
        help_text=_("Mark as featured project")
    )
    
    is_published = models.BooleanField(
        _("Published"),
        default=False,
        help_text=_("Make project visible to public")
    )
    
    views_count = models.PositiveIntegerField(
        _("Views Count"),
        default=0
    )

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ProjectMember(AuditInfoModel):
    """
    Model for project team members (students)
    """
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name=_("Project")
    )
    
    full_name = models.CharField(
        _("Full Name"),
        max_length=200,
        help_text=_("Full name of the student")
    )
    
    roll_number = models.CharField(
        _("Roll Number"),
        max_length=50,
        help_text=_("Student's roll number")
    )
    
    email = models.EmailField(
        _("Email"),
        blank=True,
        help_text=_("Student's email address")
    )
    
    phone_number = models.CharField(
        _("Phone Number"),
        max_length=20,
        blank=True,
        help_text=_("Student's phone number")
    )
    
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Department"),
        help_text=_("Student's department")
    )
    
    role = models.CharField(
        _("Role"),
        max_length=100,
        default='Team Member',
        help_text=_("Role in the project (e.g., Team Leader, Developer, etc.)")
    )
    
    linkedin_url = models.URLField(
        _("LinkedIn URL"),
        blank=True,
        help_text=_("LinkedIn profile URL")
    )
    
    github_url = models.URLField(
        _("GitHub URL"),
        blank=True,
        help_text=_("GitHub profile URL")
    )

    class Meta:
        verbose_name = _("Project Member")
        verbose_name_plural = _("Project Members")
        ordering = ['id']
        unique_together = ['project', 'roll_number']

    def __str__(self):
        return f"{self.full_name} ({self.roll_number}) - {self.project.title}"


class ProjectTag(AuditInfoModel):
    """
    Tags for projects
    """
    name = models.CharField(
        _("Tag Name"),
        max_length=100,
        unique=True,
        help_text=_("Tag name")
    )
    
    slug = models.SlugField(
        _("Slug"),
        max_length=100,
        unique=True,
        help_text=_("URL slug for the tag")
    )
    
    color = models.CharField(
        _("Color"),
        max_length=7,
        default='#3B82F6',
        help_text=_("Hex color code for the tag")
    )

    class Meta:
        verbose_name = _("Project Tag")
        verbose_name_plural = _("Project Tags")
        ordering = ['name']

    def __str__(self):
        return self.name


class ProjectTagAssignment(models.Model):
    """
    Many-to-many relationship between projects and tags
    """
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tag_assignments'
    )
    
    tag = models.ForeignKey(
        ProjectTag,
        on_delete=models.CASCADE,
        related_name='project_assignments'
    )

    class Meta:
        unique_together = ['project', 'tag']
        verbose_name = _("Project Tag Assignment")
        verbose_name_plural = _("Project Tag Assignments")

    def __str__(self):
        return f"{self.project.title} - {self.tag.name}"