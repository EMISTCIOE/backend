from ckeditor.fields import RichTextField
from django.db import models
from django.utils import timezone
from django.utils.text import slugify as django_slugify
import re
from django.utils.translation import gettext_lazy as _

# Project Imports
from src.base.models import AuditInfoModel
from src.department.models import Department
from src.notice.utils import notice_media_upload_path
from src.notice.validators import validate_notice_media_file

from .constants import NOTICE_THUMBNAIL_PATH, MediaType, NoticeStatus


class NoticeCategory(AuditInfoModel):
    name = models.CharField(_("Category Name"), max_length=100, default="General")

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class Notice(AuditInfoModel):
    slug = models.SlugField(
        _("Slug"),
        max_length=255,
        help_text=_("A unique, URL-friendly identifier for this object. "),
    )
    title = models.CharField(
        _("Title"),
        max_length=200,
        blank=True,
        help_text=_("Title of the notice."),
    )
    description = RichTextField(
        _("Description"),
        blank=True,
        help_text=_("Optional detailed content or body of the notice."),
    )
    thumbnail = models.ImageField(
        upload_to=NOTICE_THUMBNAIL_PATH,
        null=True,
        blank=True,
        verbose_name=_("Thumbnail"),
        help_text=_("Optional image representing the notice."),
    )
    category = models.ForeignKey(
        NoticeCategory,
        null=True,
        on_delete=models.SET_NULL,
        related_name="category_notices",
        verbose_name=_("Notice Category"),
        help_text=_("Category to which this notice belongs."),
    )
    department = models.ForeignKey(
        Department,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Department"),
        help_text=_("Department associated with this notice."),
    )
    is_approved_by_department = models.BooleanField(
        default=False,
        verbose_name=_("Approved by Department"),
        help_text=_("Indicates whether the department has approved this notice."),
    )
    is_approved_by_campus = models.BooleanField(
        default=False,
        verbose_name=_("Approved by Campus"),
        help_text=_("Indicates whether the campus has approved this notice."),
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("Featured"),
        help_text=_("Mark this notice as featured."),
    )
    published_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Published Date"),
        help_text=_("Date when the notice was published."),
    )
    status = models.CharField(
        _("Approval Status"),
        max_length=10,
        choices=NoticeStatus.choices(),
        default=NoticeStatus.APPROVED.value,
        db_index=True,
        help_text=_("Current approval status of the notice."),
    )
    views = models.PositiveIntegerField(_("views"), default=0)
    shares = models.PositiveIntegerField(_("shares"), default=0)

    @property
    def get_author_full_name(self) -> str:
        return self.created_by.get_full_name

    def set_viewed(self) -> None:
        self.views += 1
        self.save(update_fields=["views"])

    def set_shared(self) -> None:
        self.shares += 1
        self.save(update_fields=["shares"])

    def __str__(self) -> str:
        return self.title

    def slugify(self) -> str:
        # Create a slugified base from the title (do NOT append UUID here).
        # We keep the slug simple (no UUID) and handle uniqueness elsewhere.
        if not self.title:
            base = "notice"
        else:
            cleaned = re.sub(r"[/.]+", "-", self.title)
            # Collapse multiple hyphens and strip hyphens from ends
            cleaned = re.sub(r"-+", "-", cleaned).strip("-")
            base = cleaned
        # Keep unicode characters (Nepali) in the slug so titles remain readable.
        base_slug = django_slugify(base, allow_unicode=True) or "notice"
        return base_slug

    def generate_unique_slug(self) -> str:
        """Return a slug unique across Notice table.

        This uses the base slug from `slugify()` and only appends the UUID
        when a conflict is detected (another object already uses the base).
        """
        base_slug = self.slugify()
        # If no other notice uses this slug, return it.
        if not Notice.objects.filter(slug=base_slug).exclude(pk=self.pk).exists():
            return base_slug

        # Prefer appending year to avoid UUIDs. Use published_at year if set,
        # otherwise fallback to current year.
        try:
            year = self.published_at.year if getattr(self, "published_at", None) else None
        except Exception:
            year = None

        if not year:
            from django.utils import timezone

            year = timezone.now().year

        candidate = f"{base_slug}-{year}"
        if not Notice.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
            return candidate

        # As a last resort (very rare), append a numeric suffix to ensure uniqueness
        idx = 2
        while True:
            cand = f"{candidate}-{idx}"
            if not Notice.objects.filter(slug=cand).exclude(pk=self.pk).exists():
                return cand
            idx += 1

    def save(self, *args, **kwargs):
        # Regenerate slug from title on every save (so current records
        # are always normalized from the title). If title is empty, keep
        # existing slug.
        if self.title:
            self.slug = self.generate_unique_slug()

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-published_at"]
        verbose_name = _("Notice")
        verbose_name_plural = _("Notices")
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["department"]),
            models.Index(fields=["slug"]),
        ]


class NoticeMedia(AuditInfoModel):
    """Model to store media files associated with a notice."""

    notice = models.ForeignKey(
        Notice,
        on_delete=models.CASCADE,
        related_name="medias",
        help_text=_("The notice this media is associated with."),
    )
    file = models.FileField(
        _("Media File"),
        max_length=255,
        upload_to=notice_media_upload_path,
        help_text=_("Upload an image, video, or document."),
    )
    caption = models.CharField(
        _("Caption"),
        max_length=255,
        blank=True,
        help_text=_("Caption for particular image, document or video."),
    )
    media_type = models.CharField(
        _("Media Type"),
        max_length=10,
        choices=MediaType.choices(),
        help_text=_("Type of the uploaded media."),
    )

    class Meta:
        ordering = ["created_at"]

    def clean(self):
        """Validate allowed file types based on media type."""
        validate_notice_media_file(self.file, self.media_type)

    def __str__(self) -> str:
        return f"{self.media_type} - {self.file.name}"
