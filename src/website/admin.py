#!/usr/bin/env python
from django.contrib import admin

from .models import CampusInfo, SocialMediaLink

admin.site.register(CampusInfo)
admin.site.register(SocialMediaLink)
