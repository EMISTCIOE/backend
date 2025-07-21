from rest_framework.permissions import BasePermission

from src.libs.permissions import validate_permissions


class DepartmentPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_department",
            "POST": "add_department",
            "PATCH": "edit_department",
            "DELETE": "delete_department",
        }

        return validate_permissions(request, user_permissions_dict)
