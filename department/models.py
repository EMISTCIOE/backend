from django.db import models
import uuid
from home.models import SocialMedia
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.core.validators import FileExtensionValidator


# Create your models here.

departments_enum = (
    ('DOECE', "Department of Electronics and Communication Engineering"),
    ('DOCE', "Department of Civil and Industrial Engineering"),
    ('DOAME', "Department of AutoMobile and Mechanical Engineering"),
    ('DOARCH', "Department of Architecture"),
    ('Admninistartion', "Administration"),
    ('Library', "Library"),
)

designations_enum = (
    ('CHIEF', "Campus Chief"),
    ('ASSIST_CHIEF', "Assistant Campus Chief"),
    ('HOD', "Head of Department"),
    ('DHOD', "Deputy Head of Department"),
    ('PROF', "Professor"),
    ('ASSO_PROF', "Associate Professor"),
    ('ASSIST_PROF', "Assistant Professor"),
    ('LECT', "Lecturer"),
    ('HELPING_STAFF', "Helping Staff")
)


class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, choices=(
        departments_enum), default='DOECE', unique=True)
    # name = models.CharField(max_length=100, null=False,
    # blank=False, unique=True)
    # introduction = models.TextField(null=False, blank=False)
    # description = models.TextField(null=False, blank=False)
    introduction = RichTextField()
    description = RichTextField()
    # image = models.ImageField(upload_to='images/', null=True, blank=True)
    social_media = models.ForeignKey(
        SocialMedia, on_delete=models.CASCADE, related_name='department_social_media', null=True, blank=True)
    # programs = models.TextField(null=False, blank=False) # I guess we will be having a separate program model so that this will be a foreign key (one to many relation) to that model/table
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    routine = models.ImageField(
        upload_to='media/routine/', null=True, blank=True)
    plans = models.ForeignKey(
        'PlansPolicy', on_delete=models.CASCADE, null=True, blank=True)
    profile = models.ImageField(
        upload_to='media/profile/', null=True, blank=True)

    is_academic = models.BooleanField(default=False)

    slug = models.SlugField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Project(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    name = models.CharField(max_length=255)
    description = RichTextField()
    report = models.FileField(upload_to='media/files/project',
                              validators=[FileExtensionValidator(['pdf', 'docx'])])
    published_link = models.URLField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    slug = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    slug = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class QuestionBank(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    file = models.FileField(
        upload_to='files/', validators=[FileExtensionValidator(['pdf', 'docx'])])
    subject = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.subject)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.subject} -{self.id}'


class PlansPolicy(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    description = RichTextField()

    class Meta:
        verbose_name = 'Plans and Policy'
        verbose_name_plural = 'Plans and Policies'

    def __str__(self):
        return f'Plans and Policies - ID: {self.id}'


class Student(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    name = models.CharField(max_length=255)
    roll = models.CharField(max_length=255)
    photo = models.FileField(upload_to='media/students/')
    is_cr = models.BooleanField()
    is_topper = models.BooleanField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    slug = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class FAQ(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    question = models.CharField(max_length=255)
    answer = RichTextField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f'FAQ - ID: {self.id}'


class Blog(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    title = models.CharField(max_length=255)
    description = RichTextField()
    author = models.CharField(max_length=255)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True, blank=True)

    slug = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Programs(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    name = models.CharField(max_length=255)
    description = RichTextField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Programs'

    def __str__(self):
        return self.name


class Semester(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    name = models.CharField(max_length=100)
    program = models.ForeignKey(Programs, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} - {self.program.name}'


class Subject(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    course_objective = models.TextField(blank=True, null=True)
    topics_covered = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} [{self.code}]"


class StaffMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='images/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField()
    message = models.TextField(null=True, blank=True)
    department_id = models.ForeignKey(
        Department, blank=False, null=False, on_delete=models.CASCADE)
    designation_id = models.ForeignKey(
        'Designation', blank=False, null=False, on_delete=models.CASCADE)
    social_media = models.ForeignKey(
        SocialMedia, on_delete=models.CASCADE, related_name='staff_social_media')
    # started_at = models.DateField(null=False, blank=False)
    # ended_at = models.DateField(null=True, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Designation(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    designation = models.CharField(max_length=100, choices=(
        designations_enum), null=False, blank=False)
    # started_at = models.DateField(null=False, blank=False)
    # ended_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.designation


class Society(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField()
    social_media = models.ForeignKey(
        SocialMedia, on_delete=models.CASCADE, related_name='society_social_media')
    department_id = models.ForeignKey(
        Department, blank=False, null=False, on_delete=models.CASCADE)
    founded_at = models.DateField(null=True, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Routine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    # routine_pdf = models.Field(upload_to='media/routine/')
    routine_png = models.ImageField(upload_to='media/routine/')
    # programs = models.ForeignKey(Programs, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.semester.name} - {self.semester.program.name}'
