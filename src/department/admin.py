#!/usr/bin/env python
from django.contrib import admin

from .models import (
    AcademicProgram,
    Department,
    DepartmentDownload,
    DepartmentPlanAndPolicy,
    StaffMember,
)
from src.website.models import GlobalGalleryImage, GlobalEvent, StudentClub
from src.notice.models import Notice
from src.project.models import Project
from src.research.models import Research
from src.journal.models import Article


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


class DepartmentDownloadInline(admin.TabularInline):
    model = DepartmentDownload
    extra = 0
    fields = ("title", "file", "created_at")
    readonly_fields = ("created_at",)


class PlanAndPolicyInline(admin.TabularInline):
    model = DepartmentPlanAndPolicy
    extra = 0
    fields = ("title", "file", "created_at")
    readonly_fields = ("created_at",)


class StudentClubInline(admin.TabularInline):
    model = StudentClub
    fk_name = "department"
    extra = 0
    fields = ("name", "short_description", "website_url")
    readonly_fields = ("created_at",)
    show_change_link = True


class GlobalGalleryImageInline(admin.TabularInline):
    model = GlobalGalleryImage
    fk_name = "department"
    extra = 0
    fields = ("image", "caption", "club", "global_event", "display_order")
    readonly_fields = ("created_at",)
    show_change_link = True


class NoticeInline(admin.TabularInline):
    model = Notice
    fk_name = "department"
    extra = 0
    fields = ("title", "published_at", "status")
    readonly_fields = ("published_at",)
    show_change_link = True


class GlobalEventThroughInline(admin.TabularInline):
    model = GlobalEvent.departments.through
    extra = 0
    verbose_name = "Linked Global Event"
    verbose_name_plural = "Linked Global Events"


class ProjectInline(admin.TabularInline):
    model = Project
    fk_name = "department"
    extra = 0
    fields = ("title", "project_type", "status", "supervisor_name", "academic_year")
    readonly_fields = ("created_at",)
    show_change_link = True


class ResearchInline(admin.TabularInline):
    model = Research
    fk_name = "department"
    extra = 0
    fields = ("title", "research_type", "status", "principal_investigator", "start_date")
    readonly_fields = ("created_at",)
    show_change_link = True


class ArticleInline(admin.TabularInline):
    model = Article
    fk_name = "department"
    extra = 0
    fields = ("title", "genre", "date_published", "volume", "year")
    readonly_fields = ("id",)
    show_change_link = True


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "short_name",
        "email",
        "phone_no",
        "created_at",
    ]
    search_fields = ["name", "short_name", "email"]
    list_filter = ["created_at"]
    readonly_fields = ["slug", "created_at", "updated_at"]
    inlines = [
        DepartmentDownloadInline,
        PlanAndPolicyInline,
        StudentClubInline,
        GlobalGalleryImageInline,
        NoticeInline,
        GlobalEventThroughInline,
        ProjectInline,
        ResearchInline,
        ArticleInline,
    ]
    fieldsets = (
        (
            "Department Information",
            {
                "fields": (
                    "name",
                    "short_name",
                    "slug",
                    "brief_description",
                    "detailed_description",
                    "thumbnail",
                    "email",
                    "phone_no",
                )
            },
        ),
        (
            "Audit Information",
            {
                "fields": ("created_at", "updated_at", "created_by", "updated_by"),
                "classes": ("collapse",),
            },
        ),
    )
    
    def save_model(self, request, obj, form, change):
        """Set created_by and updated_by for the Department object."""
        if not change:  # creating new object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        """Set created_by and updated_by for inline models."""
        instances = formset.save(commit=False)
        for obj in instances:
            if not obj.pk:  # new object
                obj.created_by = request.user
            obj.updated_by = request.user
            obj.save()
        formset.save_m2m()


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ("name", "designation", "department", "email")
    search_fields = ("name", "designation", "department__name")

# Duplicate admin class removed; `Department` is already registered above with
# inlines and audit-aware save_formset.
