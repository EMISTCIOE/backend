#!/usr/bin/env python
from django.contrib import admin

from src.website.utils import build_global_gallery_items

from .models import (
    CampusFeedback,
    CampusInfo,
    CampusKeyOfficial,
    CampusSection,
    CampusStaffDesignation,
    CampusUnit,
    CampusUnion,
    CampusUnionMember,
    GlobalEvent,
    GlobalGalleryImage,
    ResearchFacility,
    SocialMediaLink,
    StudentClub,
    StudentClubMember,
)


SOURCE_TYPES = [
    {"value": "union_event", "label": "Union Event"},
    {"value": "union_gallery", "label": "Union Gallery"},
    {"value": "club_gallery", "label": "Club Gallery"},
    {"value": "department_gallery", "label": "Department Gallery"},
    {"value": "global_event", "label": "Global Event"},
    {"value": "college", "label": "College Gallery"},
    {"value": "custom", "label": "Custom"},
]


@admin.register(CampusUnionMember)
class CampusUnionMemberAdmin(admin.ModelAdmin):
    list_display = ("full_name", "designation", "union", "is_active")
    search_fields = ("full_name", "designation", "union__name")
    list_filter = ("union", "is_active")


@admin.register(StudentClubMember)
class StudentClubMemberAdmin(admin.ModelAdmin):
    list_display = ("full_name", "designation", "club", "is_active")
    search_fields = ("full_name", "designation", "club__name")
    list_filter = ("club", "is_active")


@admin.register(GlobalGalleryImage)
class GlobalGalleryImageAdmin(admin.ModelAdmin):
    change_list_template = "admin/global_gallery_change_list.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        gallery_items = build_global_gallery_items()
        source_type = request.GET.get("source_type")
        search_query = request.GET.get("q", "")

        if source_type:
            gallery_items = [
                item for item in gallery_items if item["source_type"] == source_type
            ]

        if search_query:
            search_lower = search_query.lower()
            gallery_items = [
                item
                for item in gallery_items
                if search_lower in (item.get("caption") or "").lower()
                or search_lower in (item.get("source_name") or "").lower()
                or search_lower in (item.get("source_context") or "").lower()
            ]

        extra_context.update(
            {
                "gallery_items": gallery_items,
                "source_types": SOURCE_TYPES,
                "selected_source_type": source_type,
                "search_query": search_query,
            }
        )

        return super().changelist_view(request, extra_context=extra_context)


@admin.register(GlobalEvent)
class GlobalEventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "event_type",
        "location",
        "event_start_date",
        "event_end_date",
        "is_active",
    )
    search_fields = ("title", "location")
    list_filter = ("event_type", "is_active")
    fieldsets = (
        ("Event Information", {
            "fields": ("title", "description", "event_type")
        }),
        ("Date & Location", {
            "fields": ("event_start_date", "event_end_date", "location")
        }),
        ("Registration", {
            "fields": ("registration_link",)
        }),
        ("Media", {
            "fields": ("thumbnail",)
        }),
        ("Associations", {
            "fields": ("unions", "clubs", "departments"),
            "classes": ("collapse",)
        }),
    )


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
