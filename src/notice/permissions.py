from rest_framework.permissions import BasePermission

from src.libs.permissions import validate_permissions


class NoticePermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_notice",
            "POST": "add_notice",
            "PATCH": "edit_notice",
            "DELETE": "delete_notice",
        }

        return validate_permissions(request, user_permissions_dict)


class NoticeStatusUpdatePermission(BasePermission):
    """Permission class specifically for notice status updates."""

    def has_permission(self, request, view):
        user_permissions_dict = {
            "PATCH": "edit_notice_status",
        }

        return validate_permissions(request, user_permissions_dict)
