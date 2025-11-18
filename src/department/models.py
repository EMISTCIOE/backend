from ckeditor.fields import RichTextField
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

# Project Imports
from src.base.models import AuditInfoModel
from src.core.constants import (
    AcademicProgramTypes,
    SocialMediaPlatforms,
    StaffMemberTitle,
)
from src.department.constants import (
    DEPARTMENT_DOWNLOADS_FILE_PATH,
    DEPARTMENT_EVENT_FILE_PATH,
    DEPARTMENT_PLANS_FILE_PATH,
    DEPARTMENT_PROGRAM_THUMBNAIL_PATH,
    DEPARTMENT_STAFF_PHOTO_PATH,
    DEPARTMENT_THUMBNAIL_PATH,
    DepartmentDesignationChoices,
    DepartmentEventTypes,
)


class Department(AuditInfoModel):
    """Represents the different departments of campus"""

    name = models.CharField(
        _("Name"),
        max_length=100,
        help_text=_("Official name of the department."),
    )
    short_name = models.CharField(
        _("Short Name"),
        max_length=50,
        blank=True,
        help_text=_(
            "Short name or acronym for the Department. (e.g. DOEC, DOME, DOCE)",
        ),
    )
    slug = models.SlugField(
        _("Slug"),
        max_length=255,
        blank=True,
        editable=False,
        help_text=_("Auto-generated slug from the name."),
    )
    brief_description = models.TextField(
        _("Introduction"),
        blank=True,
        help_text=_("Short introduction about the department."),
    )
    detailed_description = RichTextField(
        _("Detailed Description"),
        blank=True,
        help_text=_("Detailed information and overview of the department."),
    )
    phone_no = models.CharField(
        _("Phone"),
        max_length=15,
        blank=True,
        help_text=_("Contact phone number of the department."),
    )
    email = models.EmailField(
        _("Email"),
        blank=True,
        help_text=_("Official email address of the department."),
    )
    thumbnail = models.ImageField(
        _("Department Thumbnail"),
        upload_to=DEPARTMENT_THUMBNAIL_PATH,
        null=True,
        help_text=_("Image representing the department (used on website)."),
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")

    def __str__(self) -> str:
        return self.name


class DepartmentSocialMedia(AuditInfoModel):
    """
    Model representing a social media links for a department.
    """

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="social_links",
        db_index=True,
        verbose_name=_("Department"),
    )
    platform = models.CharField(
        _("Platform"),
        max_length=20,
        choices=SocialMediaPlatforms.choices(),
        help_text=_("Select the social media platform."),
    )
    url = models.URLField(
        _("Profile URL"),
        help_text=_("URL to the respective social media profile."),
    )

    class Meta:
        verbose_name = _("Department Social Media")
        verbose_name_plural = _("Department Social Medias")
        constraints = [
            models.UniqueConstraint(
                fields=["department", "platform"],
                name="unique_department_platform",
            ),
        ]

    def __str__(self) -> str:
        return self.get_platform_display()


class AcademicProgram(AuditInfoModel):
    """Represents the different academic programs under a department"""

    name = models.CharField(
        _("Name"),
        max_length=255,
        help_text=_("Name of the academic program."),
    )
    short_name = models.CharField(
        _("Short Name"),
        max_length=50,
        blank=True,
        help_text=_("Short name or acronym for the program. (e.g. BEI, BCT)"),
    )
    slug = models.SlugField(
        _("Slug"),
        max_length=255,
        blank=True,
        editable=False,
        help_text=_("Auto-generated slug from the program name."),
    )
    description = RichTextField(
        blank=True,
        help_text=_("Detailed description of the program."),
    )
    program_type = models.CharField(
        _("Program Type"),
        max_length=20,
        choices=AcademicProgramTypes.choices(),
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="department_programs",
        db_index=True,
        help_text=_("Department this program belongs to."),
        verbose_name=_("Department"),
    )
    thumbnail = models.ImageField(
        _("Program Thumbnail"),
        upload_to=DEPARTMENT_PROGRAM_THUMBNAIL_PATH,
        null=True,
        help_text=_("Image representing the academic program."),
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Academic Program")
        verbose_name_plural = _("Academic Programs")

    def __str__(self) -> str:
        return self.name


class DepartmentDownload(AuditInfoModel):
    """
    Downloadable forms and documents for students or faculty,
    such as ID request forms or certificates.
    """

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="downloads",
        verbose_name=_("Department"),
        db_index=True,
        help_text=_("Department the download file is associated with."),
    )
    title = models.CharField(
        _("Title"),
        max_length=100,
        help_text=_("E.g. Student ID Form, Character Certificate, etc."),
    )
    file = models.FileField(
        _("File"),
        upload_to=DEPARTMENT_DOWNLOADS_FILE_PATH,
        null=True,
        help_text=_("Upload the form or downloadable file."),
    )
    description = RichTextField(_("Description"), blank=True)

    class Meta:
        verbose_name = _("Department Download")
        verbose_name_plural = _("Department Downloads")

    def __str__(self) -> str:
        return self.title


class DepartmentEvent(AuditInfoModel):
    """
    Represents a major Department-level event or festival
    (e.g. Yathartha, Utsarga, Music Fest).
    """

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name=_("Department"),
        db_index=True,
        help_text=_("Department the event is associated with."),
    )
    title = models.CharField(
        _("Title"),
        max_length=200,
        help_text=_("Name of the event or festival."),
    )
    description_short = models.TextField(
        _("Short Description"),
        max_length=500,
        help_text=_("Brief summary of the event."),
    )
    description_detailed = RichTextField(
        _("Detailed Description"),
        blank=True,
        help_text=_("Detailed information, agenda, and activities."),
    )
    event_type = models.CharField(
        _("Event Type"),
        max_length=20,
        choices=DepartmentEventTypes.choices(),
        default=DepartmentEventTypes.OTHER,
        help_text=_("Type of the event."),
    )
    event_start_date = models.DateField(
        _("Date"),
        null=True,
        help_text=_("Date the event start."),
    )
    event_end_date = models.DateField(
        _("Date"),
        null=True,
        help_text=_("Date the event end."),
    )
    thumbnail = models.ImageField(
        _("Thumbnail"),
        upload_to=DEPARTMENT_EVENT_FILE_PATH,
        null=True,
        help_text=_("Main image for the event."),
    )
    registration_link = models.URLField(
        _("Registration Link"),
        blank=True,
        null=True,
        help_text=_("Optional link for event registration or more information."),
    )
    location = models.CharField(
        _("Location"),
        max_length=200,
        blank=True,
        help_text=_("Event venue or location."),
    )
    is_approved_by_department = models.BooleanField(
        default=False,
        verbose_name=_("Approved by Department"),
        help_text=_("Indicates whether the department has approved this event."),
    )
    is_approved_by_campus = models.BooleanField(
        default=False,
        verbose_name=_("Approved by Campus"),
        help_text=_("Indicates whether the campus has approved this event."),
    )

    class Meta:
        verbose_name = _("Department Event")
        verbose_name_plural = _("Department Events")

    def __str__(self):
        return self.title


class DepartmentEventGallery(AuditInfoModel):
    """
    Images related to a Department-wide event.
    """

    event = models.ForeignKey(
        DepartmentEvent,
        on_delete=models.CASCADE,
        related_name="gallery",
        verbose_name=_("Department Event"),
    )
    image = models.ImageField(_("Image"), upload_to=DEPARTMENT_EVENT_FILE_PATH)
    caption = models.CharField(
        _("Caption"),
        max_length=255,
        blank=True,
        help_text=_("Optional caption for the image."),
    )

    class Meta:
        verbose_name = _("Department Event Image")
        verbose_name_plural = _("Department Event Gallery")

    def __str__(self):
        return self.caption or f"{self.event.title} Image"


class DepartmentPlanAndPolicy(AuditInfoModel):
    """
    Represents an individual plan or policy associated with a department.
    """

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="plans_and_policies",
        verbose_name=_("Department"),
        db_index=True,
        help_text=_("The department this plan or policy belongs to."),
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Title"),
        help_text=_("Title of the plan or policy."),
    )
    description = RichTextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Detailed description of the plan or policy."),
    )
    file = models.FileField(
        _("File"),
        upload_to=DEPARTMENT_PLANS_FILE_PATH,
        null=True,
        help_text=_("Upload the form or downloadable file."),
    )

    class Meta:
        verbose_name = _("Plan and Policy")
        verbose_name_plural = _("Plans and Policies")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title or _("(Untitled)")
