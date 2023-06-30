from django.db import models
import uuid


# Create your models here.

sections_enum = (
        ('TCIOE_HOME', "Thapathali Campus"),
        ('TCIOE_ADMINISTRATION', "Campus Administration"),
        ('TCIOE_LIBRARY', 'Campus Library'),
    )
class HomePage(models.Model):
    # multiple images
    id = models.UUIDField(primary_key=True ,default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, default='TCIOE', choices=(sections_enum), unique=True, )
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
    name = models.CharField(max_length=100, default="doece-social", unique=True, blank=False, null=False)
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
    name = models.CharField(max_length=200, blank=False, null=False, unique=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    social_media = models.ForeignKey(SocialMedia, on_delete=models.CASCADE, related_name='unit_social_media', null=True, blank=True)
    # social_media = models.ManyToManyField(SocialMedia, related_name='unit_social_media', null=True, blank=True)

    def __str__(self):
        return self.name
    
class Resource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, blank=False, null=False, unique=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    file = models.FileField(upload_to='files/', null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ImageGallery(models.Model):
    pass