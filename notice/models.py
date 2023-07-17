from django.db import models
import uuid
from department.models import Department
from django.utils import timezone
from ckeditor.fields import RichTextField
from django.core.validators import FileExtensionValidator

# Create your models here.


class NoticeType(models.Model):
    type_enum = (
        ('Department', "Department"),
        ('Administration', "Administration"),
        ('Admission', "Admission"),
        ('Exam', "Examination"),
        ('Scholarship', "Scholarship"),
        ('Event', "Event"),
        ('Society', "Society"),
        ('Club', "Club"),
        ('Other', "Other"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notice_type = models.CharField(
        max_length=100, choices=type_enum, unique=True, null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.notice_type


class NoticeCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notice_type = models.ForeignKey(
        NoticeType, blank=False, null=False, on_delete=models.CASCADE, related_name='notice_type_set')
    category = models.CharField(
        max_length=100, null=False, blank=False, default="General")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.notice_type.notice_type) + "-" + self.category


class Notice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=250, null=False,
                            blank=False, unique=True, editable=False)
    title = models.CharField(max_length=200, null=False, blank=False)
    description = RichTextField()
    thumbnail = models.ImageField(upload_to='images/', null=True, blank=True)
    download_file = models.FileField(
        upload_to='files/', null=True, blank=True, validators=[FileExtensionValidator(['pdf',])])
    notice_category = models.ForeignKey(
        NoticeCategory, blank=True, null=True, on_delete=models.CASCADE, related_name='notice_category_set')
    department = models.ForeignKey(
        Department, blank=True, null=True, on_delete=models.CASCADE)
    is_featured = models.BooleanField(default=False, null=False, blank=False)
    published_date = models.DateField(default=timezone.now)
    modified = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def slugify(self):
        # slugify and add the id to the end of the slug
        slug = self.title.replace(" ", "-")
        return slug + "-" + str(self.id)

    def save(self, *args, **kwargs):
        # if the slug is empty then generate the slug
        if not self.slug:
            self.slug = self.slugify()
        super(Notice, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-published_date']
