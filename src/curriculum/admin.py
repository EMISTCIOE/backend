from django.contrib import admin

from .models import Routine, Subject, Suggestion

# Register your models here.


@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    list_display = ["__str__", "id"]


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ["__str__", "semester", "program", "id"]


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ["__str__", "date", "name"]
