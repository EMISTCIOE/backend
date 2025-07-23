from rest_framework.permissions import BasePermission

from src.libs.permissions import validate_permissions


class CampusInfoPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_campus_info",
            "POST": "add_campus_info",
            "PATCH": "edit_campus_info",
            "DELETE": "delete_campus_info",
        }

        return validate_permissions(request, user_permissions_dict)
