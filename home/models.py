from django.db import models
import uuid
from ckeditor.fields import RichTextField
from django.core.validators import FileExtensionValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.text import slugify

# Create your models here.

sections_enum = (
    ("TCIOE_HOME", "Thapathali Campus"),
    ("TCIOE_ADMINISTRATION", "Campus Administration"),
    ("TCIOE_LIBRARY", "Campus Library"),
)


class HomePage(models.Model):
    # multiple images
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        default="TCIOE",
        choices=(sections_enum),
        unique=True,
    )
    slider_image1 = models.ImageField(
        upload_to="images/", null=True, blank=True)
    slider_image2 = models.ImageField(
        upload_to="images/", null=True, blank=True)
    slider_image3 = models.ImageField(
        upload_to="images/", null=True, blank=True)
    slider_image4 = models.ImageField(
        upload_to="images/", null=True, blank=True)
    description = RichTextField(null=True, blank=True)
    phone_one = models.CharField(max_length=20, null=False, blank=False)
    phone_two = models.CharField(max_length=20, null=True, blank=True)
    phone_three = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=False, blank=False)
    video = models.FileField(upload_to="videos/", null=True, blank=True)
    video_description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


# social_enum = (
#         ('Facebook', 'Facebook'),
#         ('Twitter', 'Twitter'),
#         ('Instagram', 'Instagram'),
#         ('LinkedIn', 'LinkedIn'),
#         ('YouTube', 'YouTube'),
#         ('GitHub', 'GitHub'),
#         ('Website', 'Website'),
#     )
# class SocialMedia(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name =  models.CharField(max_length=100, default="doece-facebook", unique=True, blank=False, null=False)
#     type = models.CharField(max_length=100, choices=(social_enum), default='Facebook', unique=True)
#     link = models.URLField(null=False, blank=False)

#     class Meta:
#         unique_together = ('type', 'link')
#         abstract = True


# class DepartmentSocialMedia(SocialMedia):
#     department_id = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='department_social_media')

#     def __str__(self):
#         return self.department_id.name + " " + self.type


# class StaffMemberSocialMedia(SocialMedia):
#     staff_member_id = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name='staff_members_social_media')

#     def __str__(self):
#         return self.department_id.name + " " + self.type


# class SocietySocialMedia(SocialMedia):
#     society_id = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='society_social_media')

#     def __str__(self):
#         return self.department_id.name + " " + self.type


class SocialMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100, default="doece-social", unique=True, blank=False, null=False
    )
    facebook = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    youtube = models.URLField(null=True, blank=True)
    github = models.URLField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name


class Unit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, blank=False,
                            null=False, unique=True)
    description = RichTextField(null=True, blank=True)
    image = models.ImageField(upload_to="images/", null=True, blank=True)
    social_media = models.OneToOneField(
        SocialMedia,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="unit_social",
    )
    # social_media = models.ManyToManyField(SocialMedia, related_name='unit_social_media', null=True, blank=True)

    def __str__(self):
        return self.name


class Resource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        max_length=200, blank=False, null=False, unique=True)
    description = RichTextField(null=True, blank=True)
    image = models.ImageField(upload_to="images/", null=True, blank=True)
    file = models.FileField(upload_to="files/", null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    upload_date = models.DateTimeField(auto_now_add=True)
    is_downloadable = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-upload_date"]


class ImageGallery(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    description = RichTextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Image(models.Model):
    gallery = models.ForeignKey(
        ImageGallery, null=True, on_delete=models.SET_NULL)
    image = models.ImageField(upload_to="gallery/", null=False, blank=False)

    def __str__(self):
        return self.gallery.name


calendar_for = [
    ("Bachelors in Engineering", "B.E."),
    ("Masters in Engineering", "Msc"),
]


class Calendar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, null=False)
    calendar_level = models.CharField(
        choices=calendar_for, max_length=100, null=False)
    calendar_pdf = models.FileField(
        upload_to="media/calendars/",
        null=True,
        blank=True,
        validators=[FileExtensionValidator(["pdf"])],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(null=True, blank=True)
    academic_year = models.IntegerField(
        validators=[
            MinValueValidator(2075),
            MaxValueValidator(3000),
        ]
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-academic_year"]


class ReportType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Report(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=255, null=True, blank=True)
    file = models.FileField(
        upload_to="media/reports/",
        null=True,
        blank=True,
        validators=[FileExtensionValidator(["pdf", "docx"])],
    )
    type = models.ForeignKey(ReportType, null=False, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-uploaded_at"]
