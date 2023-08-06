from django.db import models
import uuid
from home.models import SocialMedia
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.core.validators import FileExtensionValidator


# Create your models here.

departments_enum = [("Department of Electronics and Computer Engineering", 'DOECE'), ("Department of Civil Engineering", 'DOCE'), ("Department of Industrial Engineering", 'DOIE'), (
    "Department of AutoMobile and Mechanical Engineering", 'DOAME'), ("Department of Architecture", 'DOARCH'), ("Department od Applied Science", 'DOAS'), ("Administration", 'Admninistartion'), ("Library", 'Library')]


designation_enums = [
    ('CHIEF', 'Campus Chief'),
    ('ASSIST_CAMPUS_CHIEF_ADMIN', 'Assistant Campus Chief (Administration)'),
    ('ASSIST_CAMPUS_CHIEF_ACADEMIC', 'Assistant Campus Chief (Academic)'),
    ('ASSIST_CAMPUS_CHIEF_PLANNING',
     'Assistant Campus Chief (Planning and Resource Management)'),
    ('HOD', 'Head of Department'),
    ('DHOD', 'Deputy Head of Department'),
    ('MSC_COORD_INFORMATION',
     'Program Coordinator, M.Sc. in Informatics and Intelligent Systems Engineering'),
    ('MSC_COORD_EARTHQUAKE', 'Program Coordinato, M.Sc. in Earthquake Engineering'),
    ('MSC_COORD_DESIGN', 'Program Coordinato, M.Sc. in Mechanical Design and Manufacturing'),
    ('EMIS_HEAD', 'Head, Education Management Information Systems'),
    ('RESEARCH_HEAD', 'Head, Research and Development Unit'),
    ('MATERIAL_HEAD', 'Head, Material Testing Laboratory'),
    ('CONSULTANCY_HEAD', 'Head, Consultancy Services'),
    ('EXAMS_ACADEMIC_HEAD', 'Examination and Academic Administration Head'),
    ('LIBRARY_HEAD', 'Head, Library Section'),
    ('FINANCE_HEAD', 'Head, Financial Administation Section'),
    ('PERSONNEL_HEAD', 'Head, Personnel Section'),
    ('GENERAL_HEAD', 'Head, General Administration Section'),
    ('PLANNING_HEAD', 'Head, Planning Section'),
    ('PROCUREMENT_HEAD', 'Head, Procurement Section'),
    ('SECURITY_HEAD', 'Head, Security Section'),
    ('REPAIR_HEAD', 'Head, Repair and Maintenance Section'),
    ('IQAC_HEAD', 'Head, IQAC Section'),
    ('SAT_HEAD', 'Head, SAT Section'),
    ('ADMINISTRATION_HEAD', 'Head, Academic Administration and Exam Section'),
    ('STORE_HEAD', 'Head, Store Section'),
    ('ACCOUNT_HEAD', 'Head, Account Section'),
    ('LECTURER', 'Lecturer'),
    ('SENIOR_INSTRUCTOR', 'Senior Instructor'),
    ('TEACHING_ASSISTANCE', 'Teaching Assistance'),
    ('INSTRUCTOR', 'Instructor'),
    ('READER', 'Reader'),
    ('PROFESSOR', 'Professor'),
    ('ASSOCIATE_PROFESSOR', 'Associate Professor'),
    ('DEPUTY_INSTRUCTOR', 'Deputy Instructor'),
    ('ASSISTANT_INSTRUCTOR', 'Assistant Instructor'),
    ('ASSISTANT_PROFESSOR', 'Assistant Professor'),
    ('ASSISTANT_FINANCE_CONTROLLER', 'Assistant Finance Controller'),
    ('DEPUTY_ADM_OFFICER', 'Deputy ADM Officer'),
    ('DEPUTY_FINANCE_CONTROLLER', 'Deputy Finance Controller'),
    ('SECTION_OFFICER', 'Section Officer'),
    ('CHIEF_OFFICE_ASSISTANT', 'Chief Office Assistant'),
    ('HEAD_ACCOUNT_ASSISTANCE', 'Head Account Assistance'),
    ('LIBRARY_ASSISTANT', 'Library Assistant'),
    ('OFFICE_ASSISTANT', 'Office Assistant'),
    ('TECHNICAL_ASSISTANT', 'Technical Assistant'),
    ('DRIVER', 'Driver'),
    ('SENIOR_OFFICE_HELPER', 'Senior Office Helper'),
    ('OFFICE_HELPER', 'Office Helper'),
    ('HEAD_TECHNICAL_ASSISTANT', 'Head Technical Assistant'),
    ('ASSISTANT_STOREKEEPER', 'Assistant Storekeeper'),
    ('COMPUTER_OPERATOR', 'Computer Operator'),
    ('LIBRARIAN', 'Librarian'),
    ('LABORATORY_ASSISTANT', 'Laboratory Assistant'),
    ('ACCOUNT_OFFICER', 'Account Officer'),
    ('LIBRARY_INTERN', 'Library Intern'),
    ('SECURITY_GUARD', 'Security Guard'),
    ('SISTER', 'Sister'),
]


class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, choices=(
        departments_enum), default='DOECE', unique=True)
    slug = models.SlugField(max_length=255, null=True,
                            blank=True, editable=False)
    introduction = RichTextField()
    description = RichTextField()
    social_media = models.ForeignKey(
        SocialMedia, on_delete=models.CASCADE, related_name='department_social_media', null=True, blank=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    routine = models.ImageField(
        upload_to='media/routine/', null=True, blank=True)
    plans = models.ForeignKey(
        'PlansPolicy', on_delete=models.CASCADE, null=True, blank=True, related_name="department_plans")
    profile = models.ImageField(
        upload_to='media/profile/', null=True, blank=True)

    is_academic = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Project(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, null=True,
                            blank=True, editable=False)
    description = RichTextField()
    report = models.FileField(upload_to='media/files/project',
                              validators=[FileExtensionValidator(['pdf', 'docx'])])
    published_link = models.URLField(null=True, blank=True)
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name='department_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class QuestionBank(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=255, null=True,
                            blank=True, editable=False)
    file = models.FileField(
        upload_to='files/', validators=[FileExtensionValidator(['pdf', 'docx'])])
    subject = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.subject)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.subject} -{self.id}'


class PlansPolicy(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    name = models.CharField(max_length=100, null=True, blank=True)
    description = RichTextField()

    class Meta:
        verbose_name = 'Plans and Policy'
        verbose_name_plural = 'Plans and Policies'

    def __str__(self):
        return f'Plans and Policies - Name: {self.name} ID: {self.id}'


class Student(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, null=True,
                            blank=True, editable=False)
    roll = models.CharField(max_length=255)
    photo = models.FileField(
        upload_to='media/students/', null=True, blank=True)
    is_cr = models.BooleanField()
    is_topper = models.BooleanField()
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='student_department')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_department(self):
        return self.department_id.name


class FAQ(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    question = models.CharField(max_length=255)
    answer = RichTextField()
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='faq_department')

    def __str__(self):
        return f'FAQ - ID: {self.id}'


class Blog(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, null=True,
                            blank=True, editable=False)
    description = RichTextField()
    author = models.CharField(max_length=255)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True, blank=True, related_name='blog_department')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Programs(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    slug = models.SlugField(max_length=255, null=True,
                            blank=True, editable=False)
    name = models.CharField(max_length=255)
    description = RichTextField()
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='department_programs')

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
    slug = models.SlugField(max_length=255, null=True,
                            blank=True, editable=False)
    name = models.CharField(max_length=100)
    program = models.ForeignKey(
        Programs, on_delete=models.CASCADE, related_name='semesters')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} - {self.program.name}'


class Subject(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    slug = models.SlugField(max_length=255, null=True,
                            blank=True, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, related_name='subjects')

    course_objective = RichTextField()
    topics_covered = RichTextField()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} [{self.code}]"

    def get_semester(self):
        return self.semester.name


class StaffMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, null=True,
                            blank=True, editable=False)
    responsibility = models.CharField(max_length=100, null=True, blank=True)
    photo = models.ImageField(upload_to='images/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField()
    message = RichTextField(null=True, blank=True)
    department = models.ForeignKey(
        Department, blank=False, null=False, on_delete=models.CASCADE, related_name='staff_members')
    designation = models.ForeignKey(
        'Designation', blank=True, null=True, on_delete=models.SET_NULL, related_name='associated_person')
    is_key_official = models.BooleanField(default=False)
    social_media = models.ForeignKey(
        SocialMedia, on_delete=models.SET_NULL, related_name='socials', null=True, blank=True)

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
        verbose_name_plural = 'Staff Members'
        ordering = ['-designation_id']
        unique_together = ['name', 'designation']


class Designation(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,  editable=False)
    designation = models.CharField(
        max_length=100, choices=designation_enums)
    rank = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.get_designation_display()

    class Meta:
        verbose_name_plural = 'Designations'
        ordering = ['rank']
        unique_together = ['designation', 'rank']


class Society(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, null=True,
                            blank=True, editable=False)
    description = models.TextField(null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField()
    social_media = models.ForeignKey(
        SocialMedia, on_delete=models.CASCADE, related_name='society_social_media')
    department_id = models.ForeignKey(
        Department, blank=False, null=False, on_delete=models.CASCADE, related_name='society_department')
    founded_at = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_department(self):
        return self.department_id.name


class Routine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, related_name='routine_semester')
    # routine_pdf = models.Field(upload_to='media/routine/')
    routine_png = models.ImageField(upload_to='media/routine/')
    # programs = models.ForeignKey(Programs, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.semester.name} - {self.semester.program.name}'
