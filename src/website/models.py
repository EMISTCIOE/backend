from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

# Project Imports
from src.base.models import AuditInfoModel, PublicAuditInfoModel
from src.core.constants import (
    AcademicProgramTypes,
    SocialMediaPlatforms,
    StaffMemberTitle,
)
from src.core.models import FiscalSessionBS
from src.department.models import Department
from src.website.constants import (
    ACADEMIC_CALENDER_FILE_PATH,
    CAMPUS_DOWNLOADS_FILE_PATH,

    CAMPUS_FILE_PATH,
    CAMPUS_KEY_OFFICIAL_FILE_PATH,
    CAMPUS_REPORT_FILE_PATH,
    CAMPUS_UNION_FILE_PATH,
    CAMPUS_UNION_MEMBER_FILE_PATH,
    CAMPUS_SECTION_FILE_PATH,
    CAMPUS_UNIT_FILE_PATH,
    GLOBAL_EVENT_FILE_PATH,
    RESEARCH_FACILITY_FILE_PATH,

    STUDENT_CLUB_FILE_PATH,
    STUDENT_CLUB_MEMBER_FILE_PATH,
    CampusEventTypes,
    ReportTypes,
    GLOBAL_GALLERY_FILE_PATH,
)
from src.website.messages import ONLY_ONE_CAMPUS_INFO_ALLOWED
from src.website.utils import nepali_year_choices


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
        upload_to=CAMPUS_FILE_PATH,
        null=True,
        blank=True,
        help_text=_("Image representing campus organizational structure."),
    )

    class Meta:
        verbose_name = _("Campus Info")
        verbose_name_plural = _("Campus Info")

    def save(self, *args, **kwargs):
        if (
            not self.pk
            and CampusInfo.objects.filter(is_active=True, is_archived=False).exists()
        ):
            raise ValidationError(ONLY_ONE_CAMPUS_INFO_ALLOWED)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CampusStaffDesignation(AuditInfoModel):
    """
    Represents campus-level staff designations/roles.
    """

    title = models.CharField(
        _("Title"),
        max_length=150,
        unique=True,
        help_text=_("Human readable name of the designation, e.g., Campus Chief."),
    )
    code = models.CharField(
        _("Code"),
        max_length=150,
        unique=True,
        help_text=_(
            "System identifier generated from the title (used in APIs and references)."
        ),
    )
    description = models.TextField(
        _("Description"),
        blank=True,
        help_text=_("Optional notes about the responsibilities of this designation."),
    )
    display_order = models.PositiveSmallIntegerField(
        _("Display Order"),
        default=1,
        help_text=_("Ordering weight when listing designations."),
    )
    is_active = models.BooleanField(
        _("Is Active"),
        default=True,
        help_text=_("Inactive designations will be hidden from selection lists."),
    )

    class Meta:
        verbose_name = _("Campus Designation")
        verbose_name_plural = _("Campus Designations")
        ordering = ["display_order", "title"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.code:
            base_code = slugify(self.title).replace("-", "_").upper()
            candidate = base_code or "DESIGNATION"
            suffix = 1
            while (
                CampusStaffDesignation.objects.exclude(pk=self.pk)
                .filter(code=candidate)
                .exists()
            ):
                candidate = f"{base_code}_{suffix}"
                suffix += 1
            self.code = candidate
        super().save(*args, **kwargs)


class CampusKeyOfficial(AuditInfoModel):
    """
    Campus staff members (includes officials and supporting team).
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
    designation = models.ForeignKey(
        CampusStaffDesignation,
        on_delete=models.PROTECT,
        related_name="staff_members",
        verbose_name=_("Designation"),
        help_text=_("Select the role for this staff member."),
        limit_choices_to={"is_active": True},
    )
    display_order = models.PositiveSmallIntegerField(
        _("Display Order"),
        default=1,
        help_text=_("Display Order (ranking) of staffs to display in website."),
    )
    is_key_official = models.BooleanField(
        _("Is Key Official"),
        default=True,
        help_text=_(
            "Mark true if this staff member should appear in key official listings."
        ),
    )
    message = models.TextField(_("Message"), blank=True)
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
        verbose_name = _("Campus Key Staffs")
        verbose_name_plural = _("Campus Staffs")

    def __str__(self):
        designation_title = (
            self.designation.title if getattr(self, "designation", None) else ""
        )
        return f"{self.title_prefix} {self.full_name} ({designation_title})"


class SocialMediaLink(AuditInfoModel):
    platform = models.CharField(
        _("Platform"),
        max_length=20,
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
    Academic calendar for a specific program type (Bachelor's or Master's) and academic year range.
    Example: 2081 Mangshir to 2082 Mangshir.
    """

    program_type = models.CharField(
        _("Program Type"),
        max_length=20,
        choices=AcademicProgramTypes.choices(),
    )
    start_year = models.PositiveIntegerField(
        _("Start Year"),
        choices=nepali_year_choices(),
        help_text=_("Start year of the academic calendar (e.g., 2081)."),
    )
    end_year = models.PositiveIntegerField(
        _("End Year"),
        choices=nepali_year_choices(),
        help_text=_("End year of the academic calendar (e.g., 2082)."),
    )
    file = models.FileField(
        _("File"),
        upload_to=ACADEMIC_CALENDER_FILE_PATH,
        null=True,
        help_text=_("Upload the academic calendar file."),
    )

    class Meta:
        verbose_name = _("Academic Calendar")
        verbose_name_plural = _("Academic Calendars")

    def __str__(self):
        return f"{self.program_type} - {self.start_year}/{self.end_year}"


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
    short_description = models.TextField(
        _("Short Description"),
        max_length=500,
        help_text=_("Brief summary or introduction (max 500 characters)."),
    )
    detailed_description = RichTextField(
        _("Detailed Description"),
        blank=True,
        help_text=_(
            "In-depth overview about the unions's mission, activities, and history.",
        ),
    )
    website_url = models.URLField(
        _("Website Link"),
        null=True,
        blank=True,
        help_text=_("URL of the club website (optional)"),
    )
    thumbnail = models.ImageField(
        _("Thumbnail"),
        upload_to=CAMPUS_UNION_FILE_PATH,
        null=True,
        help_text=_("Optional representative image or logo of the union."),
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="campus_unions",
        verbose_name=_("Linked Department"),
        help_text=_("Optional department associated with this union."),
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
        upload_to=CAMPUS_UNION_MEMBER_FILE_PATH,
        null=True,
        help_text=_("Profile photo of the member."),
    )

    class Meta:
        verbose_name = _("Union Member")
        verbose_name_plural = _("Union Members")

    def __str__(self):
        return f"{self.full_name} - {self.designation}"


class CampusSection(AuditInfoModel):
    """
    Represents an administrative/academic section within the campus hierarchy.
    Stores descriptive content, objectives and hero assets shown on the website.
    """

    name = models.CharField(
        _("Section Name"),
        max_length=150,
        unique=True,
    )
    slug = models.SlugField(
        _("Slug"),
        max_length=160,
        unique=True,
        help_text=_("Used for public URLs, e.g. /about/sections/<slug>."),
    )
    short_description = models.TextField(
        _("Short Description"),
        max_length=500,
        help_text=_("Brief summary shown in listing cards."),
    )
    detailed_description = RichTextField(
        _("Detailed Description"),
        blank=True,
        help_text=_("Rich text content describing objectives and responsibilities."),
    )
    objectives = RichTextField(
        _("Objectives"),
        blank=True,
        help_text=_("Bullet list or paragraph describing goals of the section."),
    )
    achievements = RichTextField(
        _("Key Achievements"),
        blank=True,
        help_text=_("Optional highlights, milestones or services."),
    )
    thumbnail = models.ImageField(
        _("Thumbnail"),
        upload_to=CAMPUS_SECTION_FILE_PATH,
        null=True,
        blank=True,
        help_text=_("Image used in listing cards."),
    )
    hero_image = models.ImageField(
        _("Hero Image"),
        upload_to=CAMPUS_SECTION_FILE_PATH,
        null=True,
        blank=True,
        help_text=_("Large banner image used on the section detail page."),
    )
    location = models.CharField(
        _("Location"),
        max_length=200,
        blank=True,
    )
    contact_email = models.EmailField(
        _("Email"),
        blank=True,
    )
    contact_phone = models.CharField(
        _("Phone Number"),
        max_length=30,
        blank=True,
    )
    display_order = models.PositiveSmallIntegerField(
        _("Display Order"),
        default=1,
        help_text=_("Controls ordering in menus and listing views."),
    )
    designations = models.JSONField(
        _("Linked Designations"),
        default=list,
        blank=True,
        help_text=_(
            "Staff designations responsible for this section (uses campus staff records)."
        ),
    )
    department_head = models.ForeignKey(
        "CampusKeyOfficial",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="headed_sections",
        help_text=_("Primary key official leading this section."),
    )
    members = models.ManyToManyField(
        "CampusKeyOfficial",
        blank=True,
        related_name="campus_sections",
        help_text=_("Key officials actively assigned to this section."),
    )

    class Meta:
        verbose_name = _("Campus Section")
        verbose_name_plural = _("Campus Sections")
        ordering = ["display_order", "name"]

    def __str__(self) -> str:
        return self.name


class CampusUnit(AuditInfoModel):
    """
    Represents campus level units such as EMIS, R&D, Consultancy etc.
    """

    name = models.CharField(_("Unit Name"), max_length=150, unique=True)
    slug = models.SlugField(
        _("Slug"),
        max_length=160,
        unique=True,
        help_text=_("Used for public URLs, e.g. /about/units/<slug>."),
    )
    short_description = models.TextField(
        _("Short Description"),
        max_length=500,
        help_text=_("Summary displayed in cards and hero section."),
    )
    detailed_description = RichTextField(
        _("Detailed Description"),
        blank=True,
        help_text=_("History, responsibilities and services of the unit."),
    )
    objectives = RichTextField(
        _("Objectives"),
        blank=True,
        help_text=_("List of objectives/goals shown on the public page."),
    )
    achievements = RichTextField(
        _("Key Achievements"),
        blank=True,
        help_text=_("Optional achievements, milestones or services."),
    )
    thumbnail = models.ImageField(
        _("Thumbnail"),
        upload_to=CAMPUS_UNIT_FILE_PATH,
        null=True,
        blank=True,
        help_text=_("Image used in listing cards and menus."),
    )
    hero_image = models.ImageField(
        _("Hero Image"),
        upload_to=CAMPUS_UNIT_FILE_PATH,
        null=True,
        blank=True,
        help_text=_("Primary image displayed on the detail page."),
    )
    location = models.CharField(_("Location"), max_length=200, blank=True)
    contact_email = models.EmailField(_("Email"), blank=True)
    contact_phone = models.CharField(
        _("Phone Number"),
        max_length=30,
        blank=True,
    )
    display_order = models.PositiveSmallIntegerField(
        _("Display Order"),
        default=1,
    )
    designations = models.JSONField(
        _("Linked Designations"),
        default=list,
        blank=True,
        help_text=_(
            "Staff designations responsible for this unit (uses campus staff records)."
        ),
    )
    department_head = models.ForeignKey(
        "CampusKeyOfficial",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="headed_units",
        help_text=_("Primary person responsible for this unit."),
    )
    members = models.ManyToManyField(
        "CampusKeyOfficial",
        blank=True,
        related_name="campus_units",
        help_text=_("Key officials actively working with this unit."),
    )

    class Meta:
        verbose_name = _("Campus Unit")
        verbose_name_plural = _("Campus Units")
        ordering = ["display_order", "name"]

    def __str__(self) -> str:
        return self.name


class ResearchFacility(AuditInfoModel):
    """Represents research facilities available at the campus."""

    name = models.CharField(
        _("Facility Name"),
        max_length=200,
        unique=True,
        help_text=_("Name of the research facility."),
    )
    slug = models.SlugField(
        _("Slug"),
        max_length=220,
        unique=True,
        blank=True,
        help_text=_("Auto-generated slug used for URLs."),
    )
    short_description = models.TextField(
        _("Short Description"),
        max_length=500,
        blank=True,
        help_text=_("Brief summary displayed in listings."),
    )
    description = RichTextField(
        _("Description"),
        blank=True,
        help_text=_("Full description for the facility."),
    )
    objectives = RichTextField(
        _("Objectives"),
        blank=True,
        help_text=_("Key goals or focus areas for the facility."),
    )
    thumbnail = models.ImageField(
        _("Image"),
        upload_to=RESEARCH_FACILITY_FILE_PATH,
        null=True,
        blank=True,
        help_text=_("Image used in listings and detail view."),
    )
    display_order = models.PositiveSmallIntegerField(
        _("Display Order"),
        default=1,
        help_text=_("Ordering weight for public listings."),
    )

    class Meta:
        verbose_name = _("Research Facility")
        verbose_name_plural = _("Research Facilities")
        ordering = ["display_order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


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
    website_url = models.URLField(
        _("Website Link"),
        null=True,
        blank=True,
        help_text=_("URL of the club website (optional)"),
    )
    thumbnail = models.ImageField(
        _("Thumbnail"),
        upload_to=STUDENT_CLUB_FILE_PATH,
        null=True,
        help_text=_("Optional representative image or logo of the club."),
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_clubs",
        verbose_name=_("Linked Department"),
        help_text=_("Optional department associated with this student club."),
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
        upload_to=STUDENT_CLUB_MEMBER_FILE_PATH,
        null=True,
        help_text=_("Profile photo of the member."),
    )

    class Meta:
        verbose_name = _("Club Member")
        verbose_name_plural = _("Club Members")

    def __str__(self):
        return f"{self.full_name} ({self.designation})"



class GlobalEvent(AuditInfoModel):
    """
    Centralized event that can be linked to unions, clubs, or departments.
    """

    title = models.CharField(
        _("Event Title"),
        max_length=255,
        help_text=_("Name of the event."),
    )
    description = RichTextField(
        _("Description"),
        blank=True,
        help_text=_("Detail the event activities and insights."),
    )
    event_type = models.CharField(
        _("Event Type"),
        max_length=20,
        choices=CampusEventTypes.choices(),
        default=CampusEventTypes.OTHER,
        help_text=_("Type of the event."),
    )
    event_start_date = models.DateField(
        _("Event Start Date"),
        null=True,
        blank=True,
        help_text=_("Date when the event starts."),
    )
    event_end_date = models.DateField(
        _("Event End Date"),
        null=True,
        blank=True,
        help_text=_("Date when the event ends."),
    )
    thumbnail = models.ImageField(
        _("Thumbnail"),
        upload_to=GLOBAL_EVENT_FILE_PATH,
        null=True,
        blank=True,
        help_text=_("Representative banner for the event."),
    )
    unions = models.ManyToManyField(
        "CampusUnion",
        blank=True,
        related_name="global_events",
        verbose_name=_("Linked Unions"),
        help_text=_("Associate unions with this event."),
    )
    clubs = models.ManyToManyField(
        "StudentClub",
        blank=True,
        related_name="global_events",
        verbose_name=_("Linked Clubs"),
        help_text=_("Associate student clubs with this event."),
    )
    departments = models.ManyToManyField(
        Department,
        blank=True,
        related_name="global_events",
        verbose_name=_("Linked Departments"),
        help_text=_("Associate departments with this event."),
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

    class Meta:
        verbose_name = _("Global Event")
        verbose_name_plural = _("Global Events")

    def __str__(self):
        return self.title


class GlobalGalleryImage(AuditInfoModel):
    """Images belonging to a gallery collection."""

    class SourceType(models.TextChoices):
        CAMPUS_EVENT = "campus_event", _("Campus Event")
        UNION_EVENT = "union_event", _("Union Event")
        CLUB_EVENT = "club_event", _("Student Club Event")
        GLOBAL_EVENT = "global_event", _("Global Event")
        UNION_GALLERY = "union_gallery", _("Union Gallery")
        CLUB_GALLERY = "club_gallery", _("Club Gallery")
        DEPARTMENT_GALLERY = "department_gallery", _("Department Gallery")
        UNIT_GALLERY = "unit_gallery", _("Campus Unit Gallery")
        SECTION_GALLERY = "section_gallery", _("Campus Section Gallery")
        COLLEGE = "college", _("College Gallery")
        CUSTOM = "custom", _("Custom Gallery")

    source_type = models.CharField(
        _("Source Type"),
        max_length=32,
        choices=SourceType.choices,
        default=SourceType.COLLEGE,
        help_text=_("Primary source category applied to this image."),
    )
    source_title = models.CharField(
        _("Source Title"),
        max_length=255,
        blank=True,
        help_text=_("Optional title or headline describing the source."),
    )
    source_context = models.CharField(
        _("Source Context"),
        max_length=255,
        blank=True,
        help_text=_("Optional context shown alongside this image."),
    )
    union = models.ForeignKey(
        CampusUnion,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="global_gallery_images",
        verbose_name=_("Union"),
    )
    club = models.ForeignKey(
        StudentClub,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="global_gallery_images",
        verbose_name=_("Student Club"),
    )
    department = models.ForeignKey(
        Department,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="global_gallery_images",
        verbose_name=_("Department"),
    )
    unit = models.ForeignKey(
        CampusUnit,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="global_gallery_images",
        verbose_name=_("Campus Unit"),
    )
    section = models.ForeignKey(
        CampusSection,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="global_gallery_images",
        verbose_name=_("Campus Section"),
    )
    global_event = models.ForeignKey(
        GlobalEvent,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="global_gallery_images",
        verbose_name=_("Global Event"),
    )
    image = models.ImageField(
        _("Image"),
        upload_to=GLOBAL_GALLERY_FILE_PATH,
        help_text=_("Upload an image for this gallery item."),
    )
    caption = models.CharField(
        _("Caption"),
        max_length=255,
        blank=True,
        help_text=_("Optional caption for the image."),
    )
    display_order = models.PositiveSmallIntegerField(
        _("Display Order"),
        default=1,
        help_text=_("Controls the ordering of images within the collection."),
    )

    class Meta:
        verbose_name = _("Gallery Image")
        verbose_name_plural = _("Gallery Images")
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        fallback = self.source_title or "Gallery"
        return self.caption or f"{fallback} Image"


class CampusFeedback(PublicAuditInfoModel):
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
