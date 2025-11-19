from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import (
    MainModule,
    Permission,
    PermissionCategory,
    Role,
    User,
    UserAccountVerification,
    UserForgetPasswordRequest,
)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal Info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone_no",
                    "photo",
                )
            },
        ),
        (
            _("Roles & Permissions"),
            {
                "fields": ("roles", "permissions"),
            },
        ),
        (
            _("Status"),
            {
                "fields": ("is_active", "is_archived"),
            },
        ),
        (
            _("Important Dates"),
            {
                "fields": ("last_login", "date_joined"),
            },
        ),
        (
            _("Audit"),
            {
                "fields": ("created_by", "updated_by"),
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "email",
                    "first_name",
                    "last_name",
                    "is_active",
                ),
            },
        ),
    )
    list_display = ("username", "email", "full_name", "is_active", "is_archived")
    list_filter = ("is_active", "is_archived", "roles")
    search_fields = ("username", "email", "first_name", "last_name")
    readonly_fields = ("last_login", "date_joined")
    filter_horizontal = ("roles", "permissions")

    def full_name(self, obj):
        return obj.get_full_name()

    full_name.short_description = _("Full name")


admin.site.register(Role)
admin.site.register(MainModule)
admin.site.register(PermissionCategory)
admin.site.register(Permission)
admin.site.register(UserForgetPasswordRequest)
admin.site.register(UserAccountVerification)
