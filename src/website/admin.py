#!/usr/bin/env python
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

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
from .utils import build_global_gallery_items


class GlobalGalleryAdmin(admin.ModelAdmin):
    """Custom admin for viewing aggregated global gallery from all sources."""
    change_list_template = "website/global_gallery_change_list.html"
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_site.admin_view(self.changelist_view), name='website_globalgallery_changelist'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        # Build aggregated gallery items
        gallery_items = build_global_gallery_items()
        
        # Apply filtering by source type if requested
        source_type = request.GET.get('source_type', '')
        if source_type:
            gallery_items = [item for item in gallery_items if item['source_type'] == source_type]
        
        # Apply search filtering
        search_query = request.GET.get('q', '')
        if search_query:
            search_lower = search_query.lower()
            gallery_items = [
                item for item in gallery_items
                if search_lower in (item.get('source_name') or '').lower()
                or search_lower in (item.get('caption') or '').lower()
                or search_lower in (item.get('source_context') or '').lower()
            ]
        
        # Sort by created_at (newest first)
        gallery_items.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Format items for display
        formatted_items = []
        for item in gallery_items:
            image_html = ''
            if item.get('image'):
                image_html = format_html(
                    '<img src="{}" width="100" height="100" style="object-fit: cover;"/>', 
                    item['image'].url
                )
            
            formatted_items.append({
                'uuid': item['uuid'],
                'image_html': image_html,
                'caption': item.get('caption', ''),
                'source_type': item['source_type'].replace('_', ' ').title(),
                'source_name': item.get('source_name', ''),
                'source_context': item.get('source_context', ''),
                'created_at': item['created_at'],
            })
        
        extra_context = extra_context or {}
        extra_context.update({
            'title': 'Global Gallery',
            'gallery_items': formatted_items,
            'source_types': [
                {'value': 'campus_event', 'label': 'Campus Event'},
                {'value': 'club_event', 'label': 'Club Event'},
                {'value': 'department_event', 'label': 'Department Event'},
            ],
            'selected_source_type': source_type,
            'search_query': search_query,
        })
        
        return render(request, self.change_list_template, extra_context)


# Register the aggregated gallery as a "fake" model admin
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


# Register Global Gallery (aggregated view from multiple sources)
class GlobalGalleryProxy:
    """Proxy class to register Global Gallery in admin."""
    _meta = type('_meta', (), {
        'app_label': 'website',
        'model_name': 'globalgallery',
        'verbose_name': 'Global Gallery',
        'verbose_name_plural': 'Global Gallery',
    })()


admin.site.register(GlobalGalleryProxy, GlobalGalleryAdmin)
