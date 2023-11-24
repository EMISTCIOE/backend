from django.contrib import admin
from .models import Routine, Subject

# Register your models here.


@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    list_display = ["__str__", "id"]


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ["__str__", "semester", "id"]
