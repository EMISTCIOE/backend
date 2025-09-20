from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

# Project Imports
from src.base.models import AuditInfoModel
from src.department.models import Department
from src.project_hive.constants import (
    PROJECT_MEDIA_PATH,
    PROJECT_MEMBER_IMAGE_PATH,
    LevelChoice,
    ProjectStatus,
)

User = get_user_model()


class ProjectCategory(AuditInfoModel):
    name = models.CharField(_("Category Name"), max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name


class BatchYear(AuditInfoModel):
    year = models.PositiveIntegerField(_("Batch Year"), unique=True)

    class Meta:
        ordering = ["-year"]
        verbose_name = _("Batch Year")
        verbose_name_plural = _("Batch Years")

    def __str__(self):
        return str(self.year)


class Project(AuditInfoModel):
    title = models.CharField(_("Project Title"), max_length=255)
    slug = models.SlugField(_("Slug"), max_length=265, unique=True)
    abstract = models.CharField(_("Abstract"), max_length=500)
    batch_year = models.ForeignKey(
        BatchYear,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    level = models.CharField(_("Level"), max_length=20, choices=LevelChoice.choices())
    supervisor = models.CharField(_("Supervisor"), max_length=255)
    project_details = models.TextField(_("Project Details"))
    technologies_used = models.CharField(_("Technologies Used"), max_length=1000)
    github_link = models.URLField(
        _("GitHub Link"),
        max_length=5000,
        blank=True,
        null=True,
    )
    documentation_link = models.URLField(
        _("Documentation Link"),
        max_length=5000,
        blank=True,
        null=True,
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=ProjectStatus.choices(),
        default=ProjectStatus.PENDING.value,
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="approved_projects",
    )
    views = models.BigIntegerField(_("Views"), default=0)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["department"]),
            models.Index(fields=["batch_year"]),
            models.Index(fields=["level"]),
        ]

    def __str__(self):
        return self.title


class ProjectTeamMember(AuditInfoModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="team_members",
    )
    full_name = models.CharField(_("Full Name"), max_length=1000)
    roll_no = models.CharField(_("Roll No"), max_length=50)
    photo = models.ImageField(
        _("Photo"),
        upload_to=PROJECT_MEMBER_IMAGE_PATH,
        null=True,
    )

    class Meta:
        unique_together = ("project", "roll_no")
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.roll_no})"


class ProjectFile(AuditInfoModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="files")
    file_type = models.CharField(_("File Type"), max_length=1000)
    file = models.FileField(_("File"), upload_to=PROJECT_MEDIA_PATH)

    class Meta:
        ordering = ["file_type"]

    def __str__(self):
        return f"{self.project.title} - {self.file_type}"


class ProjectRating(AuditInfoModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="ratings",
    )
    user = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        related_name="project_ratings",
    )
    rating = models.PositiveSmallIntegerField(
        _("Rating"),
        choices=[(i, str(i)) for i in range(1, 6)],
    )

    class Meta:
        unique_together = ("project", "user")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project"]),
            models.Index(fields=["user"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.project.title} - {self.rating}"


class ProjectDiscussion(AuditInfoModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="discussions",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="project_discussions",
    )
    comment = models.TextField(_("Comment"))
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="replies",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project"]),
            models.Index(fields=["user"]),
            models.Index(fields=["-created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(id=models.F("parent")),
                name="chk_parent_not_self",
            ),
        ]

    def __str__(self):
        return f"Comment by {self.user} on {self.project.title}"
