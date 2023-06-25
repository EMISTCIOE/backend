from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
import uuid


class DepartmentLogin(models.Model):
    user_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user_name


class DepartmentInfo(models.Model):
    '''
    This model is will be used for storing the information of the department 
    '''
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    name = models.CharField(max_length=255, unique=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    social = models.ForeignKey(
        'Social', on_delete=models.CASCADE, null=True, blank=True)
    # intro = models.TextField()
    intro = RichTextField()
    description = RichTextField()
    # programs = models.ManyToManyField('Programs')
    routine = models.ImageField(upload_to='media/routine/')
    plans = models.ForeignKey('PlansPolicy', on_delete=models.CASCADE)
    profile = models.ImageField(upload_to='media/profile/')
    slug = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Social(models.Model):
    '''

    This model is will be used for storing the Social Media of the department. 

    '''
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    name = models.CharField(max_length=255)
    fb = models.URLField(null=True, blank=True)
    yt = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    insta = models.URLField(null=True, blank=True)
    tiktok = models.URLField(null=True, blank=True)
    github = models.URLField(null=True, blank=True)

    def __str__(self):
        return f'{self.name}'


class Notice(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    name = models.CharField(max_length=255)
    description = RichTextField()
    file = models.FileField(upload_to='media/files/notice/')
    type_of_notice = models.ForeignKey('NoticeType', on_delete=models.CASCADE)
    department = models.ForeignKey(DepartmentInfo, on_delete=models.CASCADE)
    slug = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    slug = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class NoticeType(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    name = models.CharField(max_length=255)
    # category = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Project(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    name = models.CharField(max_length=255)
    description = RichTextField()
    report = models.FileField(upload_to='media/files/project')
    published_link = models.URLField(null=True, blank=True)
    department = models.ForeignKey(DepartmentInfo, on_delete=models.PROTECT)
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
    file = models.FileField(upload_to='files/')
    subject = models.CharField(max_length=255)

    def __str__(self):
        return f'Question Bank - ID: {self.id}'


class ImageGallery(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    image1 = models.FileField(upload_to='media/images/')
    image2 = models.FileField(upload_to='media/images/')
    image3 = models.FileField(upload_to='media/images/')
    department = models.ForeignKey(DepartmentInfo, on_delete=models.CASCADE)

    def __str__(self):
        return f'Image Gallery - ID: {self.id}'


class PlansPolicy(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    description = models.CharField(max_length=255)

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
    is_tooper = models.BooleanField()
    department = models.ForeignKey(DepartmentInfo, on_delete=models.CASCADE)

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
    department = models.ForeignKey(DepartmentInfo, on_delete=models.CASCADE)

    def __str__(self):
        return f'FAQ - ID: {self.id}'


class Blog(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    title = models.CharField(max_length=255)
    description = RichTextField()
    author = models.CharField(max_length=255)
    department = models.ForeignKey(DepartmentInfo, on_delete=models.CASCADE)

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
    department = models.ForeignKey(DepartmentInfo, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Programs'

    def __str__(self):
        return self.title


class Semester(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    name = models.CharField(max_length=100)
    program = models.ForeignKey(Programs, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Subject(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    course_objective = models.TextField(blank=True, null=True)
    topics_covered = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} [{self.code}]"
