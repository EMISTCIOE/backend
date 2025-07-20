from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

# Project Imports
from src.base.models import AuditInfoModel
from src.core.constants import (
    AcademicProgramTypes,
    DesignationChoices,
    SocialMediaPlatforms,
    StaffMemberTitle,
)
from src.department.constants import (
    DEPARTMENT_PROGRAM_THUMBNAIL_PATH,
    DEPARTMENT_STAFF_PHOTO_PATH,
    DEPARTMENT_THUMBNAIL_PATH,
)


class Department(AuditInfoModel):
    """Represents the different departments of campus"""

    name = models.CharField(
        _("Name"),
        max_length=100,
        help_text=_("Official name of the department."),
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


class SocialMediaLink(AuditInfoModel):
    """
    Model representing a social media links for a department.
    """

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="department_social_links",
        db_index=True,
        verbose_name=_("Department"),
    )
    platform = models.CharField(
        _("Platform"),
        max_length=20,
        unique=True,
        choices=SocialMediaPlatforms.choices(),
        help_text=_("Select the social media platform."),
    )
    url = models.URLField(
        _("Profile URL"),
        help_text=_("URL to the respective social media profile."),
    )

    class Meta:
        verbose_name = _("Social Media Link")
        verbose_name_plural = _("Social Media Links")

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


class StaffMember(AuditInfoModel):
    """Represents the staff members of a department."""

    title = models.CharField(
        _("Title"),
        max_length=50,
        choices=StaffMemberTitle.choices(),
        help_text=_("Title of the staff member (e.g., Mr., Dr., Prof.)."),
    )
    name = models.CharField(
        _("Name"),
        max_length=100,
        help_text=_("Full name of the staff member."),
    )
    designation = models.CharField(
        _("Designation"),
        max_length=100,
        choices=DesignationChoices.choices(),
        blank=True,
        help_text=_("Official designation or position."),
    )
    photo = models.ImageField(
        _("Photo"),
        upload_to=DEPARTMENT_STAFF_PHOTO_PATH,
        null=True,
        help_text=_("Profile picture of the staff member."),
    )
    phone_number = models.CharField(
        _("Phone Number"),
        max_length=20,
        blank=True,
        help_text=_("Contact phone number."),
    )
    email = models.EmailField(
        _("Email Address"),
        blank=True,
        help_text=_("Email address for communication."),
    )
    message = RichTextField(
        _("Message"),
        blank=True,
        help_text=_("Short message from staff (HOD) or profile bio."),
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="department_staffs",
        verbose_name=_("Department"),
        db_index=True,
        help_text=_("Department the staff member is associated with."),
    )
    program = models.ForeignKey(
        AcademicProgram,
        null=True,
        on_delete=models.SET_NULL,
        related_name="program_staffs",
        verbose_name=_("Academic Program"),
        help_text=_("Academic program the staff member is part of, if any."),
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Staff Member")
        verbose_name_plural = _("Staff Members")
