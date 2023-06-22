from django.contrib import admin
from .models import Department, StaffMember, Designation
from home.models import SocialMedia
# Register your models here.

admin.site.register(Department)
admin.site.register(StaffMember)
admin.site.register(Designation)


# from home app
admin.site.register(SocialMedia)

