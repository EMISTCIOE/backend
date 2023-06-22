from django.db import models
import uuid
from home.models import SocialMedia

# Create your models here.

departments_enum = (
        ('DOECE', "Department of Electronics and Communication Engineering"),
        ('DOCE', "Department of Civil and Industrial Engineering"),
        ('DOAME', "Department of AutoMobile and Mechanical Engineering"),
        ('DOARCH', "Department of Architecture"),
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
    name = models.CharField(max_length=100, choices=(departments_enum), default='DOECE', unique=True)
    introduction = models.TextField(null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    social_media = models.ForeignKey(SocialMedia, on_delete=models.CASCADE, related_name='department_social_media', null=True, blank=True)
    # programs = models.TextField(null=False, blank=False) # I guess we will be having a separate program model so that this will be a foreign key (one to many relation) to that model/table

    def __str__(self):
        return self.name


class StaffMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='images/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField()
    message = models.TextField(null=False, blank=False)
    department_id = models.ForeignKey(Department, blank=False, null=False, on_delete=models.CASCADE)
    designation_id = models.ForeignKey('Designation', blank=False, null=False, on_delete=models.CASCADE)
    social_media = models.ForeignKey(SocialMedia, on_delete=models.CASCADE, related_name='staff_social_media')
    started_at = models.DateField(null=False, blank=False)
    ended_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name


class Designation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,  editable=False)
    designation = models.CharField(max_length=100, choices=(designations_enum), null=False, blank=False)
    started_at = models.DateField(null=False, blank=False)
    ended_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.designation


class Society(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField() 
    social_media = models.ForeignKey(SocialMedia, on_delete=models.CASCADE, related_name='society_social_media')
    department_id = models.ForeignKey(Department, blank=False, null=False, on_delete=models.CASCADE)
    founded_at = models.DateField(null=False, blank=False)

    def __str__(self):
        return self.name

