#!/usr/bin/env python
from django.contrib import admin

from .models import (
    CampusEvent,
    CampusEventGallery,
    CampusFeedback,
    CampusInfo,
    CampusKeyOfficial,
    CampusSection,
    CampusStaffDesignation,
    CampusUnit,
    CampusUnion,
    ResearchFacility,
    SocialMediaLink,
    StudentClub,
)

admin.site.register(CampusEvent)
admin.site.register(CampusEventGallery)
admin.site.register(CampusUnion)
admin.site.register(StudentClub)
admin.site.register(CampusSection)
admin.site.register(CampusUnit)
admin.site.register(ResearchFacility)


@admin.register(CampusInfo)
class CampusInfoAdmin(admin.ModelAdmin):
    pass


@admin.register(SocialMediaLink)
class SocialMediaLinkAdmin(admin.ModelAdmin):
    list_display = ["platform", "url", "is_active"]


@admin.register(CampusStaffDesignation)
class CampusStaffDesignationAdmin(admin.ModelAdmin):
    list_display = ("title", "code", "display_order", "is_active")
    search_fields = ("title", "code")
    list_filter = ("is_active",)


@admin.register(CampusKeyOfficial)
class CampusKeyOfficialAdmin(admin.ModelAdmin):
    list_display = (
        "title_prefix",
        "full_name",
        "designation",
        "email",
        "phone_number",
        "is_key_official",
        "is_active",
    )
    search_fields = ("full_name", "designation__title", "designation__code", "email")
    list_filter = ("designation", "is_key_official", "is_active")


admin.site.register(CampusFeedback)
