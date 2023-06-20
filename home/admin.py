from django.contrib import admin
from .models import Home, SocialMedia
# Register your models here.

class SocialMediaAdmin(admin.ModelAdmin):
    list_display = ('type', 'link')
    list_filter = ('type', 'link')
    search_fields = ('type', 'link')
    ordering = ('type', 'link')

admin.site.register(Home)
admin.site.register(SocialMedia)