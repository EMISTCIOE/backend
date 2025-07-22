#!/usr/bin/env python
from django.contrib import admin

from .models import CampusInfo, SocialMediaLink, CampusDownload

admin.site.register(CampusInfo)
admin.site.register(SocialMediaLink)
admin.site.register(CampusDownload)
