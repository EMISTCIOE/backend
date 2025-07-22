#!/usr/bin/env python
from django.contrib import admin

from .models import CampusInfo, SocialMediaLink

@admin.register(CampusInfo)
class CampusInfoAdmin(admin.ModelAdmin):
    pass

@admin.register(SocialMediaLink)
class SocialMediaLinkAdmin(admin.ModelAdmin):
    list_display = ["platform", "url", "is_active"]