import uuid

from ckeditor.fields import RichTextField
from django.db import models
from django.utils.text import slugify

Programs = [
    ("Bachelor of Electronics, Information and Communication Engineering", "BEI"),
    ("Bachelor of Computer Engineering", "BCT"),
    ("Bachelor of Civil Engineering", "BCE"),
    ("Bachelor of Industrial Engineering", "BIE"),
    ("Bachelor of AutoMobile Engineering", "BAM"),
    ("Bachelor of Mechanical Engineering", "BME"),
    ("Bachelor of Architecture Engineering", "B.Arch"),
]

Semester = [
    ("I/I", "I/I"),
    ("I/II", "I/II"),
    ("II/I", "II/I"),
    ("II/II", "II/II"),
    (
        "III/I",
        "III/I",
    ),
    (
        "III/II",
        "III/II",
    ),
    (
        "IV/I",
        "IV/I",
    ),
    (
        "IV/II",
        "IV/II",
    ),
    (
        "V/I",
        "V/I",
    ),
    (
        "V/II",
        "V/II",
    ),
]


# Create your models here.
# class Semester(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     slug = models.SlugField(max_length=255, null=True, blank=True, editable=False)
#     name = models.CharField(max_length=100)

#     def save(self, *args, **kwargs):
#         self.slug = slugify(self.name)
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.name} - {self.program.name}"


class Subject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, null=True, blank=True, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    semester = models.CharField(
        max_length=200,
        choices=Semester,
        null=False,
        blank=False,
    )
    program = models.CharField(
        max_length=200,
        choices=Programs,
        null=False,
        blank=False,
    )

    # course_objective = RichTextField()
    topics_covered = RichTextField()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} [{self.code}]"

    def get_semester(self):
        return self.semester.name


class Routine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    semester = models.CharField(
        max_length=200,
        choices=Semester,
        null=False,
        blank=False,
    )
    # routine_pdf = models.Field(upload_to='media/routine/')
    routine_png = models.ImageField(upload_to="media/routine/")
    # programs = models.ForeignKey(Programs, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.semester.name} - {self.semester.program.name}"


class Suggestion(models.Model):
    name = models.CharField(null=True, blank=True, max_length=255)
    message = models.TextField(null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.message[:10]}"
