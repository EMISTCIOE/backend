# Register your models here.
from department.admin import SocialMediaInline
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
    list_display = ["title", "type", "uploaded_at"]


@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ["title", "calendar_level", "academic_year"]


class HomePageAdmin(admin.ModelAdmin):
    list_display = ("name", "phone_one", "email")
    list_filter = ("name", "phone_one", "email")
    search_fields = ("name", "phone_one", "email")


admin.site.register(HomePage, HomePageAdmin)


class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "is_featured", "upload_date")
    search_fields = ("title",)
    list_filter = ("title", "is_featured")


admin.site.register(Resource, ResourceAdmin)


class UnitAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


admin.site.register(Unit, UnitAdmin)


class ImageInline(admin.StackedInline):
    model = Image
    extra = 1


class ImageGalleryAdmin(admin.ModelAdmin):
    inlines = [ImageInline]
    list_display = [
        "name",
    ]


# admin.site.register(Image)
admin.site.register(ImageGallery, ImageGalleryAdmin)
