import uuid

from ckeditor.fields import RichTextField
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from src.base.models import AuditInfoModel


class Department(AuditInfoModel):
    """Represents the different departments of campus"""

    name = models.CharField(_("Name"), max_length=100)
    slug = models.SlugField(_("Slug"), max_length=255, blank=True, editable=False)
    brief_description = models.TextField(_("Introduction"), blank=True)
    detailed_description = RichTextField(_("Detailed Description"), blank=True)
    phone_no = models.CharField(_("Phone"), max_length=15, blank=True)
    email = models.EmailField(_("Email"), blank=True)
    thumbnail = models.ImageField(
        _("Department Thumbnail"), upload_to="media/profile/", null=True
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["is_academic"]


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, null=True, blank=True, editable=False)
    description = RichTextField(null=True, blank=True)
    report = models.FileField(
        upload_to="media/files/project",
        validators=[FileExtensionValidator(["pdf", "docx"])],
    )
    published_link = models.URLField(null=True, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="department_projects",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class QuestionBank(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True, editable=False)
    file = models.FileField(
        upload_to="files/",
        validators=[FileExtensionValidator(["pdf", "docx"])],
    )
    subject = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.subject)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subject} -{self.id}"


class PlansPolicy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, null=True, blank=True)
    description = RichTextField(null=True, blank=True)

    class Meta:
        verbose_name = "Plans and Policy"
        verbose_name_plural = "Plans and Policies"

    def __str__(self):
        return f"Plans and Policies - Name: {self.name} ID: {self.id}"


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, null=True, blank=True, editable=False)
    roll = models.CharField(max_length=255)
    photo = models.FileField(upload_to="media/students/", null=True, blank=True)
    is_cr = models.BooleanField()
    is_topper = models.BooleanField()
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="student_department",
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_department(self):
        return self.department_id.name


class FAQ(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=255)
    answer = RichTextField(null=True, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="faq_department",
    )

    def __str__(self):
        return f"FAQ - ID: {self.id}"


class Blog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, null=True, blank=True, editable=False)
    description = RichTextField(null=True, blank=True)
    author = models.CharField(max_length=255)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="blog_department",
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Programs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, null=True, blank=True, editable=False)
    name = models.CharField(max_length=255)
    description = RichTextField(null=True, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="department_programs",
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Programs"

    def __str__(self):
        return self.name


class StaffMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, null=True, blank=True, editable=False)
    responsibility = models.CharField(max_length=100, null=True, blank=True)
    photo = models.ImageField(upload_to="images/", null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField()
    message = RichTextField(null=True, blank=True)
    department = models.ForeignKey(
        Department,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name="staff_members",
    )
    designation = models.ForeignKey(
        "Designation",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="associated_person",
    )
    is_key_official = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_degisnation(self):
        return self.designation_id.designation

    def get_department(self):
        return self.department_id.name

    class Meta:
        verbose_name_plural = "Staff Members"
        ordering = ["designation"]
        unique_together = ["name", "designation"]


class Designation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rank = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.get_designation_display()

    class Meta:
        verbose_name_plural = "Designations"
        ordering = ["rank"]
        unique_together = ["designation", "rank"]


class Society(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, null=True, blank=True, editable=False)
    description = models.TextField(null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField()
    department_id = models.ForeignKey(
        Department,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name="society_department",
    )
    founded_at = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_department(self):
        return self.department_id.name
