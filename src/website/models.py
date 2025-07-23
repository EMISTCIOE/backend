from ckeditor.fields import RichTextField
from django.db import models
from django.utils.translation import gettext_lazy as _
import os
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

# Project Imports
from src.base.models import AuditInfoModel
from src.core.constants import (
    AcademicProgramTypes,
    SocialMediaPlatforms,
    StaffMemberTitle,
)
from src.core.models import FiscalSessionBS
from src.website.constants import (
    ACADEMIC_CALENDER_FILE_PATH,
    CAMPUS_DOWNLOADS_FILE_PATH,
    CAMPUS_KEY_OFFICIAL_FILE_PATH,
    CAMPUS_REPORT_FILE_PATH,
    CAMPUS_UNION_FILE_PATH,
    STUDENT_CLUB_FILE_PATH,
    CampusDesignationChoices,
    CampusEventTypes,
    ReportTypes,
)


class CampusInfo(AuditInfoModel):
    """
    Basic information about the campus including contact details and org chart.
    """

    name = models.CharField(
        _("Campus Name"),
        max_length=200,
        unique=True,
        help_text=_("Name of the campus."),
    )
    phone_number = models.CharField(
        _("Phone Number"),
        max_length=20,
        blank=True,
        help_text=_("Main contact phone number."),
    )
    email = models.EmailField(
        _("Email Address"),
        blank=True,
        help_text=_("General contact email."),
    )
    location = models.CharField(
        _("Location"),
        max_length=300,
        blank=True,
        help_text=_("Physical address or location of the campus."),
    )
    organization_chart = models.ImageField(
        _("Organization Chart"),
        upload_to="campus/org_charts/",
        null=True,
        blank=True,
        help_text=_("Image representing campus organizational structure."),
    )

    class Meta:
        verbose_name = _("Campus Info")
        verbose_name_plural = _("Campus Info")

    def save(self, *args, **kwargs):
        if not self.pk and CampusInfo.objects.filter(is_active=True, is_archived=False).exists():
            raise Exception("Only one active CampusInfo instance allowed!")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CampusKeyOfficial(AuditInfoModel):
    """
    Key officials members of the campus (campus staffs).
    """

    title_prefix = models.CharField(
        _("Title Prefix"),
        choices=StaffMemberTitle.choices(),
        max_length=10,
        help_text=_("E.g., ER, DR, Mr., Ms."),
    )
    full_name = models.CharField(
        _("Full Name"),
        max_length=100,
    )
    designation = models.CharField(
        _("Designation"),
        choices=CampusDesignationChoices.choices(),
        max_length=100,
        help_text=_("Role or position, e.g., Campus Chief."),
    )
    photo = models.ImageField(
        _("Photo"),
        upload_to=CAMPUS_KEY_OFFICIAL_FILE_PATH,
        null=True,
        blank=True,
    )
    email = models.EmailField(
        _("Email"),
        blank=True,
        help_text=_("Official email address."),
    )
    phone_number = models.CharField(
        _("Phone Number"),
        max_length=20,
        blank=True,
        help_text=_("Contact phone number."),
    )

    class Meta:
        verbose_name = _("Campus Key Official")
        verbose_name_plural = _("Campus Key Officials")

    def __str__(self):
        return f"{self.title_prefix} {self.full_name} ({self.designation})"


class SocialMediaLink(AuditInfoModel):
    platform = models.CharField(
        _("Platform"),
        max_length=20,
        unique=True,
        choices=SocialMediaPlatforms.choices(),
        help_text=_("Select the social media platform."),
    )
    url = models.URLField(
        _("Platform URL"),
        help_text=_("URL to the respective social media profile."),
    )
    class Meta:
        verbose_name = _("Social Media Link")
        verbose_name_plural = _("Social Media Links")

    def __str__(self) -> str:
        return f"{self.get_platform_display()}: {self.url}"


class AcademicCalendar(AuditInfoModel):
    """
    Academic calendar for a specific program type (Bachelor's or Master's) and year.
    """

    program_type = models.CharField(
        _("Program Type"),
        max_length=20,
        choices=AcademicProgramTypes.choices(),
    )
    year = models.PositiveIntegerField(_("Year"))
    file = models.FileField(
        _("File"),
        upload_to=ACADEMIC_CALENDER_FILE_PATH,
        null=True,
        help_text=_("Upload the academic calendar file."),
    )

    class Meta:
        verbose_name = _("Academic Calendar")
        verbose_name_plural = _("Academic Calendars")


class CampusReport(AuditInfoModel):
    """
    Annual or self-study report published by the campus, organized by fiscal year.
    """

    report_type = models.CharField(
        _("Report Type"),
        max_length=20,
        choices=ReportTypes.choices(),
    )
    fiscal_session = models.ForeignKey(
        FiscalSessionBS,
        on_delete=models.PROTECT,
        verbose_name=_("Fiscal Session"),
        related_name="campus_reports",
        help_text=_("Select the fiscal session for this report."),
    )
    published_date = models.DateField(
        _("Published Date"),
        null=True,
        help_text=_("Date the report was officially published."),
    )
    file = models.FileField(
        _("File"),
        upload_to=CAMPUS_REPORT_FILE_PATH,
        null=True,
        help_text=_("Upload the report file."),
    )

    class Meta:
        verbose_name = _("Campus Report")
        verbose_name_plural = _("Campus Reports")


class CampusDownload(AuditInfoModel):
    """
    Downloadable forms and documents for
    students or faculty, such as ID request forms or certificates.
    """

    title = models.CharField(
        _("Title"),
        max_length=100,
        help_text=_("E.g. Student ID Form, Character Certificate, etc."),
    )
    file = models.FileField(
        _("File"),
        upload_to=CAMPUS_DOWNLOADS_FILE_PATH,
        null=True,
        help_text=_("Upload the form or downloadable file."),
    )
    description = RichTextField(_("Description"), blank=True)

    class Meta:
        verbose_name = _("Campus Download")
        verbose_name_plural = _("Campus Downloads")

    def __str__(self) -> str:
        return self.title


class CampusEvent(AuditInfoModel):
    """
    Represents a major campus-level event or festival
    (e.g. Saraswati Puja, Yathartha, Utsarga, Music Fest).
    """

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
        choices=CampusEventTypes.choices(),
        default=CampusEventTypes.OTHER,
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
        upload_to="campus/events/thumbnails/",
        null=True,
        help_text=_("Main image for the event."),
    )

    class Meta:
        verbose_name = _("Campus Event")
        verbose_name_plural = _("Campus Events")

    def __str__(self):
        return self.title


class CampusEventGallery(AuditInfoModel):
    """
    Images related to a campus-wide event.
    """

    event = models.ForeignKey(
        CampusEvent,
        on_delete=models.CASCADE,
        related_name="gallery",
        verbose_name=_("Campus Event"),
    )
    image = models.ImageField(
        _("Image"),
        upload_to="campus/events/gallery/",
    )
    caption = models.CharField(
        _("Caption"),
        max_length=255,
        blank=True,
        help_text=_("Optional caption for the image."),
    )

    class Meta:
        verbose_name = _("Campus Event Image")
        verbose_name_plural = _("Campus Event Gallery")

    def __str__(self):
        return self.caption or f"{self.event.title} Image"


class CampusUnion(AuditInfoModel):
    """
    Represents a union or association within the campus,
    such as Free Student Union, Teachers' Union, or Staff Union.
    """

    name = models.CharField(
        _("Union Name"),
        max_length=100,
        help_text=_("Name of the union, e.g. Free Student Union"),
    )
    description = RichTextField(
        _("Description"),
        blank=True,
        help_text=_("Details or objectives of the union."),
    )

    class Meta:
        verbose_name = _("Campus Union")
        verbose_name_plural = _("Campus Unions")

    def __str__(self):
        return self.name


class CampusUnionMember(AuditInfoModel):
    """
    Represents an individual member of a campus union,
    including their name and designation.
    """

    union = models.ForeignKey(
        CampusUnion,
        on_delete=models.CASCADE,
        related_name="members",
        verbose_name=_("Union"),
        help_text=_("Union to which this member belongs."),
    )
    full_name = models.CharField(
        _("Full Name"),
        max_length=100,
        help_text=_("Full name of the union member."),
    )
    designation = models.CharField(
        _("Designation"),
        max_length=100,
        help_text=_("Member's role or title, e.g. President, Secretary, Treasurer."),
    )
    photo = models.ImageField(
        _("Photo"),
        upload_to=CAMPUS_UNION_FILE_PATH,
        null=True,
        help_text=_("Profile photo of the member."),
    )

    class Meta:
        verbose_name = _("Union Member")
        verbose_name_plural = _("Union Members")

    def __str__(self):
        return f"{self.full_name} - {self.designation}"


class StudentClub(AuditInfoModel):
    """
    Represents a student club on campus such as AMESIN, Tensor, ECAST, RAC, SOES, etc.
    """

    name = models.CharField(
        _("Club Name"),
        max_length=100,
        unique=True,
        help_text=_("Name of the student club, e.g. AMESIN, Tensor, etc."),
    )
    short_description = models.TextField(
        _("Short Description"),
        max_length=500,
        help_text=_("Brief summary or introduction (max 500 characters)."),
    )
    detailed_description = RichTextField(
        _("Detailed Description"),
        blank=True,
        help_text=_(
            "In-depth overview about the club's mission, activities, and history.",
        ),
    )
    thumbnail = models.ImageField(
        _("Thumbnail"),
        upload_to="clubs/thumbnails/",
        null=True,
        help_text=_("Optional representative image or logo of the club."),
    )

    class Meta:
        verbose_name = _("Student Club")
        verbose_name_plural = _("Student Clubs")

    def __str__(self):
        return self.name


class StudentClubMember(AuditInfoModel):
    """
    Represents a member of a student club, with photo and designation.
    """

    club = models.ForeignKey(
        StudentClub,
        on_delete=models.CASCADE,
        related_name="members",
        verbose_name=_("Club"),
    )
    full_name = models.CharField(
        _("Full Name"),
        max_length=100,
        help_text=_("Full name of the club member."),
    )
    designation = models.CharField(
        _("Designation"),
        max_length=100,
        help_text=_("Position or role, e.g. President, Vice-President, Coordinator."),
    )
    photo = models.ImageField(
        _("Photo"),
        upload_to=STUDENT_CLUB_FILE_PATH,
        null=True,
        help_text=_("Profile photo of the member."),
    )

    class Meta:
        verbose_name = _("Club Member")
        verbose_name_plural = _("Club Members")

    def __str__(self):
        return f"{self.full_name} ({self.designation})"


class StudentClubEvent(AuditInfoModel):
    """
    Represents an event organized or participated in by a student club.
    """

    club = models.ForeignKey(
        StudentClub,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name=_("Club"),
    )
    title = models.CharField(
        _("Event Title"),
        max_length=200,
        help_text=_("Title of the event."),
    )
    description = RichTextField(
        _("Event Description"),
        blank=True,
        help_text=_("Details about the event, purpose, and activities."),
    )
    date = models.DateField(
        _("Event Date"),
        null=True,
        blank=True,
        help_text=_("Date when the event took place."),
    )
    thumbnail = models.ImageField(
        _("Event Thumbnail"),
        upload_to="clubs/events/thumbnails/",
        null=True,
        blank=True,
        help_text=_("Representative image for the event."),
    )

    class Meta:
        verbose_name = _("Club Event")
        verbose_name_plural = _("Club Events")

    def __str__(self):
        return f"{self.title} ({self.club.name})"


class StudentClubEventGallery(AuditInfoModel):
    """
    Image gallery for student clubs to showcase events, projects, or achievements.
    """

    event = models.ForeignKey(
        StudentClubEvent,
        on_delete=models.CASCADE,
        related_name="gallery",
        verbose_name=_("Event"),
    )
    image = models.ImageField(
        _("Image"),
        upload_to="clubs/gallery/",
        help_text=_("Upload an image to showcase."),
    )
    caption = models.CharField(
        _("Caption"),
        max_length=255,
        blank=True,
        help_text=_("Optional caption describing the image."),
    )

    class Meta:
        verbose_name = _("Club Event Gallery Image")
        verbose_name_plural = _("Club Event Gallery Images")

    def __str__(self):
        return self.caption or f"{self.event.title} Image"


class CampusFeedback(AuditInfoModel):
    """
    Model to collect feedback or suggestions from campus students and visitors.
    """

    full_name = models.CharField(_("Full Name"), max_length=100)
    roll_number = models.CharField(_("Roll Number"), max_length=30, blank=True)
    email = models.EmailField(_("Email"), blank=True)
    message = models.TextField(_("Feedback or Suggestion"))
    is_resolved = models.BooleanField(_("Resolved"), default=False)

    class Meta:
        verbose_name = _("Campus Feedback")
        verbose_name_plural = _("Campus Feedbacks")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - Feedback"

@receiver(pre_delete, sender=CampusKeyOfficial)
def delete_photo_file_on_delete(sender, instance, **kwargs):
    if instance.photo and instance.photo.name:
        instance.photo.delete(save=False)

@receiver(pre_save, sender=CampusKeyOfficial)
def delete_old_photo_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_instance = CampusKeyOfficial.objects.get(pk=instance.pk)
    except CampusKeyOfficial.DoesNotExist:
        return
    old_file = old_instance.photo
    new_file = instance.photo
    if old_file and old_file != new_file:
        old_file.delete(save=False)
