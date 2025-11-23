from ckeditor.fields import RichTextField
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from src.base.models import AuditInfoModel
from src.department.models import AcademicProgram, Department

RESEARCH_STATUS_CHOICES = [
    ("proposed", _("Proposed")),
    ("ongoing", _("Ongoing")),
    ("completed", _("Completed")),
    ("published", _("Published")),
    ("cancelled", _("Cancelled")),
]

RESEARCH_TYPE_CHOICES = [
    ("basic", _("Basic Research")),
    ("applied", _("Applied Research")),
    ("experimental", _("Experimental")),
    ("theoretical", _("Theoretical")),
    ("review", _("Review/Survey")),
    ("case_study", _("Case Study")),
    ("other", _("Other")),
]

PARTICIPANT_TYPE_CHOICES = [
    ("faculty", _("Faculty")),
    ("staff", _("Staff")),
    ("student", _("Student")),
    ("external", _("External Collaborator")),
]


class Research(AuditInfoModel):
    """
    Model for research projects
    """

    title = models.CharField(
        _("Research Title"),
        max_length=300,
        help_text=_("Title of the research"),
    )

    slug = models.SlugField(
        _("Slug"),
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text=_("URL-friendly identifier for the research"),
    )

    description = RichTextField(
        _("Research Description"),
        help_text=_("Detailed description of the research"),
        blank=True,
    )

    abstract = models.TextField(
        _("Abstract"),
        help_text=_("Brief abstract of the research"),
        blank=True,
    )

    research_type = models.CharField(
        _("Research Type"),
        max_length=20,
        choices=RESEARCH_TYPE_CHOICES,
        default="applied",
    )

    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=RESEARCH_STATUS_CHOICES,
        default="proposed",
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Department"),
        help_text=_("Primary department (optional)"),
    )

    academic_program = models.ForeignKey(
        AcademicProgram,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="research_items",
        verbose_name=_("Academic Program"),
        help_text=_("Link to a specific academic program (optional)"),
    )

    principal_investigator = models.CharField(
        _("Principal Investigator"),
        max_length=200,
        help_text=_("Name of the principal investigator"),
    )

    pi_email = models.EmailField(
        _("PI Email"),
        help_text=_("Email of the principal investigator"),
    )

    start_date = models.DateField(_("Start Date"), null=True, blank=True)

    end_date = models.DateField(_("End Date"), null=True, blank=True)

    funding_agency = models.CharField(
        _("Funding Agency"),
        max_length=200,
        blank=True,
        help_text=_("Name of the funding agency"),
    )

    funding_amount = models.DecimalField(
        _("Funding Amount"),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Total funding amount"),
    )

    keywords = models.TextField(
        _("Keywords"),
        blank=True,
        help_text=_("Research keywords (comma separated)"),
    )

    methodology = RichTextField(
        _("Methodology"),
        blank=True,
        help_text=_("Research methodology"),
    )

    expected_outcomes = RichTextField(
        _("Expected Outcomes"),
        blank=True,
        help_text=_("Expected research outcomes"),
    )

    publications_url = models.URLField(
        _("Publications URL"),
        blank=True,
        help_text=_("URL to publications/papers"),
    )

    project_url = models.URLField(
        _("Project URL"),
        blank=True,
        help_text=_("Project website URL"),
    )

    github_url = models.URLField(
        _("GitHub URL"),
        blank=True,
        help_text=_("GitHub repository URL"),
    )

    report_file = models.FileField(
        _("Research Report"),
        upload_to="research/reports/",
        blank=True,
        help_text=_("Upload research report PDF"),
    )

    thumbnail = models.ImageField(
        _("Thumbnail"),
        upload_to="research/thumbnails/",
        blank=True,
        help_text=_("Research thumbnail image"),
    )

    is_featured = models.BooleanField(
        _("Featured Research"),
        default=False,
        help_text=_("Mark as featured research"),
    )

    is_published = models.BooleanField(
        _("Published"),
        default=False,
        help_text=_("Make research visible to public"),
    )

    views_count = models.PositiveIntegerField(_("Views Count"), default=0)

    class Meta:
        verbose_name = _("Research")
        verbose_name_plural = _("Research")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def _generate_unique_slug(self):
        base_slug = slugify(self.slug or self.title) or "research"
        candidate = base_slug
        counter = 2

        while (
            Research.objects.filter(slug=candidate)
            .exclude(pk=self.pk)
            .exists()
        ):
            candidate = f"{base_slug}-{counter}"
            counter += 1

        return candidate

    def save(self, *args, **kwargs):
        # Generate slug only when missing to avoid breaking existing links.
        if self.title and not self.slug:
            self.slug = self._generate_unique_slug()
        elif self.slug:
            # Normalize provided slug and keep it unique.
            self.slug = self._generate_unique_slug()

        super().save(*args, **kwargs)


class ResearchParticipant(AuditInfoModel):
    """
    Model for research participants (faculty, staff, students, external)
    """

    research = models.ForeignKey(
        Research,
        on_delete=models.CASCADE,
        related_name="participants",
        verbose_name=_("Research"),
    )

    full_name = models.CharField(
        _("Full Name"),
        max_length=200,
        help_text=_("Full name of the participant"),
    )

    participant_type = models.CharField(
        _("Participant Type"),
        max_length=20,
        choices=PARTICIPANT_TYPE_CHOICES,
        help_text=_("Type of participant"),
    )

    email = models.EmailField(
        _("Email"),
        blank=True,
        help_text=_("Participant's email address"),
    )

    phone_number = models.CharField(
        _("Phone Number"),
        max_length=20,
        blank=True,
        help_text=_("Participant's phone number"),
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Department"),
        help_text=_("Participant's department"),
    )

    designation = models.CharField(
        _("Designation"),
        max_length=200,
        blank=True,
        help_text=_("Job title/designation"),
    )

    # For students
    roll_number = models.CharField(
        _("Roll Number"),
        max_length=50,
        blank=True,
        help_text=_("Student's roll number (if applicable)"),
    )

    # For external collaborators
    organization = models.CharField(
        _("Organization"),
        max_length=200,
        blank=True,
        help_text=_("Organization name (for external collaborators)"),
    )

    role = models.CharField(
        _("Role"),
        max_length=100,
        default="Researcher",
        help_text=_("Role in the research project"),
    )

    linkedin_url = models.URLField(
        _("LinkedIn URL"),
        blank=True,
        help_text=_("LinkedIn profile URL"),
    )

    orcid_id = models.CharField(
        _("ORCID ID"),
        max_length=50,
        blank=True,
        help_text=_("ORCID identifier"),
    )

    is_corresponding_author = models.BooleanField(
        _("Corresponding Author"),
        default=False,
        help_text=_("Is this the corresponding author?"),
    )

    class Meta:
        verbose_name = _("Research Participant")
        verbose_name_plural = _("Research Participants")
        ordering = ["id"]

    def __str__(self):
        return f"{self.full_name} ({self.participant_type}) - {self.research.title}"


class ResearchCategory(AuditInfoModel):
    """
    Categories for research
    """

    name = models.CharField(
        _("Category Name"),
        max_length=100,
        unique=True,
        help_text=_("Category name"),
    )

    slug = models.SlugField(
        _("Slug"),
        max_length=100,
        unique=True,
        help_text=_("URL slug for the category"),
    )

    description = models.TextField(
        _("Description"),
        blank=True,
        help_text=_("Category description"),
    )

    color = models.CharField(
        _("Color"),
        max_length=7,
        default="#10B981",
        help_text=_("Hex color code for the category"),
    )

    class Meta:
        verbose_name = _("Research Category")
        verbose_name_plural = _("Research Categories")
        ordering = ["name"]

    def __str__(self):
        return self.name


class ResearchCategoryAssignment(models.Model):
    """
    Many-to-many relationship between research and categories
    """

    research = models.ForeignKey(
        Research,
        on_delete=models.CASCADE,
        related_name="category_assignments",
    )

    category = models.ForeignKey(
        ResearchCategory,
        on_delete=models.CASCADE,
        related_name="research_assignments",
    )

    class Meta:
        unique_together = ["research", "category"]
        verbose_name = _("Research Category Assignment")
        verbose_name_plural = _("Research Category Assignments")

    def __str__(self):
        return f"{self.research.title} - {self.category.name}"


class ResearchPublication(AuditInfoModel):
    """
    Publications related to research
    """

    research = models.ForeignKey(
        Research,
        on_delete=models.CASCADE,
        related_name="publications",
        verbose_name=_("Research"),
    )

    title = models.CharField(
        _("Publication Title"),
        max_length=300,
        help_text=_("Title of the publication"),
    )

    journal_conference = models.CharField(
        _("Journal/Conference"),
        max_length=200,
        help_text=_("Name of journal or conference"),
    )

    publication_date = models.DateField(_("Publication Date"), null=True, blank=True)

    doi = models.CharField(
        _("DOI"),
        max_length=100,
        blank=True,
        help_text=_("Digital Object Identifier"),
    )

    url = models.URLField(
        _("Publication URL"),
        blank=True,
        help_text=_("Link to the publication"),
    )

    citation_count = models.PositiveIntegerField(
        _("Citation Count"),
        default=0,
        help_text=_("Number of citations"),
    )

    class Meta:
        verbose_name = _("Research Publication")
        verbose_name_plural = _("Research Publications")
        ordering = ["-publication_date"]

    def __str__(self):
        return f"{self.title} - {self.journal_conference}"
