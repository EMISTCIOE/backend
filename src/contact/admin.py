from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from src.contact.models import PhoneNumber


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ['department_name', 'phone_number', 'display_order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['department_name', 'phone_number', 'description']
    list_editable = ['display_order', 'is_active']
    ordering = ['display_order', 'department_name']
    
    fieldsets = (
        (_("Contact Information"), {
            'fields': ('department_name', 'phone_number', 'description', 'display_order')
        }),
        (_("Status"), {
            'fields': ('is_active', 'is_archived')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by', 'uuid']
        if obj:  # editing an existing object
            return readonly_fields
        return readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:  # creating new object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)