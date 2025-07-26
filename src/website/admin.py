#!/usr/bin/env python
from django.contrib import admin

from .models import (
    CampusInfo,
    CampusKeyOfficial,
    SocialMediaLink,
    CampusEvent,
    CampusEventGallery,
    CampusReport,
    FiscalSessionBS,
)


@admin.register(FiscalSessionBS)
class FiscalSessionBSAdmin(admin.ModelAdmin):
    list_display = ["session_full", "session_short"]
    search_fields = ["session_full", "session_short"]


@admin.register(CampusEvent)
class CampusEventAdmin(admin.ModelAdmin):
    list_display = ["title", "event_type", "event_start_date", "is_active"]


@admin.register(CampusReport)
class CampusReportAdmin(admin.ModelAdmin):
    list_display = ["report_type", "fiscal_session", "published_date", "is_active"]
    list_filter = ["fiscal_session", "report_type", "is_active"]
    search_fields = ["report_type"]


admin.site.register(CampusEventGallery)


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
