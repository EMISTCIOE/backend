from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register([DepartmentLogin, Social,
                    PlansPolicy, Semester])
admin.site.register([NoticeType, Project, QuestionBank,
                    ImageGallery, Student, FAQ, Blog, Subject])

# admin.site.register([Resource,Syllabus])


@admin.register(DepartmentInfo)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'id']


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['name', 'type_of_notice', 'department', 'id']


@admin.register(Programs)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'id']
