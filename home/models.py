from django.db import models
import uuid

# Create your models here.

class Home(models.Model):
    # multiple images
    name = models.CharField(max_length=100, default='TCIOE', unique=True, editable=False)
    slider_image1 = models.ImageField(upload_to='images/', null=True, blank=True)
    slider_image2 = models.ImageField(upload_to='images/', null=True, blank=True)
    slider_image3 = models.ImageField(upload_to='images/', null=True, blank=True)
    slider_image4 = models.ImageField(upload_to='images/', null=True, blank=True)
    description = models.TextField(null=False, blank=False)
    phone_one = models.CharField(max_length=20, null=False, blank=False)
    phone_two = models.CharField(max_length=20, null=True, blank=True)
    phone_three = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=False, blank=False)
    video = models.FileField(upload_to='videos/', null=True, blank=True)
    video_description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class SocialMedia(models.Model):
    social_enum = (
        ('Facebook', 'Facebook'),
        ('Twitter', 'Twitter'),
        ('Instagram', 'Instagram'),
        ('LinkedIn', 'LinkedIn'),
        ('YouTube', 'YouTube'),
        ('GitHub', 'GitHub'),
        ('Website', 'Website'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name =  models.CharField(max_length=100, default="doece-facebook", unique=True, blank=False, null=False)
    type = models.CharField(max_length=100, choices=(social_enum), default='Facebook', unique=True)
    link = models.URLField(null=False, blank=False)

    class Meta:
        unique_together = ('type', 'link')

    def __str__(self):
        return self.name
    
