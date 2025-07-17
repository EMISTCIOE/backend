# Register your models here.
from django.contrib import admin

from .models import (
    Calendar,
    HomePage,
    Image,
    ImageGallery,
    Report,
    ReportType,
    Resource,
    Unit,
)

admin.site.register(ReportType)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["title", "type", "created_at"]  
    list_filter = ["type", "created_at"]
    search_fields = ["title", "slug"]
    ordering = ["-created_at"]


@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ["title", "calendar_level", "academic_year", "created_at"]
    list_filter = ["calendar_level", "academic_year"]
    search_fields = ["title"]
    ordering = ["-academic_year"]


class HomePageAdmin(admin.ModelAdmin):
    list_display = ("name", "phone_one", "email", "created_at")
    list_filter = ("name", "created_at")
    search_fields = ("name", "phone_one", "email")


admin.site.register(HomePage, HomePageAdmin)


class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "is_featured", "created_at")  # Changed from "upload_date"
    search_fields = ("title",)
    list_filter = ("is_featured", "created_at")  # Added created_at filter
    ordering = ["-created_at"]


admin.site.register(Resource, ResourceAdmin)


class UnitAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    list_filter = ("created_at",)


admin.site.register(Unit, UnitAdmin)


class ImageInline(admin.StackedInline):
    model = Image
    extra = 1


class ImageGalleryAdmin(admin.ModelAdmin):
    inlines = [ImageInline]
    list_display = ["name", "created_at"]
    ordering = ["-created_at"]


admin.site.register(ImageGallery, ImageGalleryAdmin)
