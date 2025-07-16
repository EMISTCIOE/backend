from rest_framework.permissions import BasePermission

from src.libs.permissions import validate_permissions


class EmailConfigPermission(BasePermission):
    def has_permission(self, request, view):
        ROLE_METHOD_MAP = {
            "SAFE_METHODS": ["CMS-ADMIN"],
            "POST": ["CMS-ADMIN"],
            "PATCH": ["CMS-ADMIN"],
            "DELETE": ["CMS-ADMIN"],
        }

        return validate_permissions(request, ROLE_METHOD_MAP)
