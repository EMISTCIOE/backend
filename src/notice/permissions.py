from rest_framework.permissions import BasePermission

from src.libs.permissions import validate_permissions


class NoticePermission(BasePermission):
    def has_permission(self, request, view):
        ROLE_METHOD_MAP = {
            "SAFE_METHODS": ["CMS-ADMIN", "CONTENT-EDITOR"],
            "POST": ["CMS-ADMIN", "CONTENT-EDITOR"],
            "PATCH": ["CMS-ADMIN", "CONTENT-EDITOR"],
            "DELETE": ["CMS-ADMIN", "CONTENT-EDITOR"],
        }

        return validate_permissions(request, ROLE_METHOD_MAP)
