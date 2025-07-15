from django.contrib import admin
from src.home.models import SocialMedia

from .models import *
from .models import Department, Designation, StaffMember

# Register your models here.


# admin.site.register(Department)
# admin.site.register(StaffMember)


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ["name", "designation", "department", "phone_number", "email"]
    search_fields = ["name", "designation__designation", "email"]


admin.site.register(Designation)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["name", "department", "roll", "is_cr", "is_topper"]
    search_fields = ["name", "department", "roll", "is_cr", "is_topper"]


class SocialMediaInline(admin.StackedInline):
    model = SocialMedia


# from home app
admin.site.register(SocialMedia)

admin.site.register([PlansPolicy])
admin.site.register([FAQ, Blog])

# admin.site.register([Resource,Syllabus])


@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ["__str__", "id"]
    search_fields = ["subject"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "department", "published_link", "id"]


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "email", "id"]
    search_fields = ["name", "phone", "email"]


# @admin.register(Notice)
# class NoticeAdmin(admin.ModelAdmin):
#     list_display = ['name', 'type_of_notice', 'department', 'id']


@admin.register(Programs)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ["name", "department", "id"]
    search_fields = ["name", "department"]
