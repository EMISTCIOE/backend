from rest_framework.permissions import BasePermission

from src.libs.permissions import validate_permissions


class UserSetupPermission(BasePermission):
    ROLE_METHOD_MAP = {
        "SAFE_METHODS": ["viewer", "editor", "admin"],
        "POST": ["admin"],
        "PATCH": ["editor", "admin"],
        "DELETE": ["admin"],
    }

    def has_permission(self, request, view):
        return validate_permissions(request, self.ROLE_METHOD_MAP)


class RoleSetupPermission(BasePermission):
    ROLE_METHOD_MAP = {
        "SAFE_METHODS": ["viewer", "editor", "admin"],
        "POST": ["admin"],
        "PATCH": ["editor", "admin"],
        "DELETE": ["admin"],
    }

    def has_permission(self, request, view):
        return validate_permissions(request, self.ROLE_METHOD_MAP)
