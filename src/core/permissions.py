from rest_framework.permissions import BasePermission

from src.libs.permissions import validate_permissions


class EmailConfigPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_email_config",
            "POST": "add_email_config",
            "PATCH": "edit_email_config",
            "DELETE": "delete_email_config",
        }

        return validate_permissions(request, user_permissions_dict)
