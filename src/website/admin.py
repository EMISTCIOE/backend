#!/usr/bin/env python
from django.contrib import admin

from .models import (
    CampusEvent,
    CampusEventGallery,
    CampusFeedback,
    CampusInfo,
    CampusKeyOfficial,
    CampusSection,
    CampusUnit,
    CampusUnion,
    SocialMediaLink,
    StudentClub,
)

admin.site.register(CampusEvent)
admin.site.register(CampusEventGallery)
admin.site.register(CampusUnion)
admin.site.register(StudentClub)
admin.site.register(CampusSection)
admin.site.register(CampusUnit)


@admin.register(CampusInfo)
class CampusInfoAdmin(admin.ModelAdmin):
    pass


@admin.register(SocialMediaLink)
class SocialMediaLinkAdmin(admin.ModelAdmin):
    list_display = ["platform", "url", "is_active"]


@admin.register(CampusKeyOfficial)
class CampusKeyOfficialAdmin(admin.ModelAdmin):
    list_display = (
        "title_prefix",
        "full_name",
        "designation",
        "email",
        "phone_number",
        "is_active",
    )
    search_fields = ("full_name", "designation", "email")
    list_filter = ("designation", "is_active")


admin.site.register(CampusFeedback)
