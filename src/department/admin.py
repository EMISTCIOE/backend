#!/usr/bin/env python
from django.contrib import admin

from .models import AcademicProgram, Department


@admin.register(AcademicProgram)
class AcademicProgramAdmin(admin.ModelAdmin):
    list_display = ["name", "short_name", "program_type", "department", "created_at"]
    list_filter = ["program_type", "department", "created_at"]
    search_fields = ["name", "short_name", "description"]
    readonly_fields = ["slug", "created_at", "updated_at"]
    fieldsets = (
        ("Program Information", {
            "fields": ("name", "short_name", "slug", "description", "program_type")
        }),
        ("Department", {
            "fields": ("department",)
        }),
        ("Media", {
            "fields": ("thumbnail",)
        }),
        ("Audit Information", {
            "fields": ("created_at", "updated_at", "created_by", "updated_by"),
            "classes": ("collapse",)
        }),
    )


admin.site.register(Department)
