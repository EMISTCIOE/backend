from rest_framework.permissions import BasePermission

from src.libs.permissions import validate_permissions
from src.user.constants import EMIS_STAFF_ROLE


class UserSetupPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_user",
            "POST": "add_user",
            "PATCH": "edit_user",
            "DELETE": "delete_user",
        }

        return validate_permissions(request, user_permissions_dict)


class RoleSetupPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_user_role",
            "POST": "add_user_role",
            "PATCH": "edit_user_role",
            "DELETE": "delete_user_role",
        }

        return validate_permissions(request, user_permissions_dict)


def _user_has_role(user, allowed_roles: set[str]) -> bool:
    if not user or user.is_anonymous:
        return False
    if user.is_superuser:
        return True
    # Check both the primary role field and any assigned role objects
    primary_role = getattr(user, "role", None)
    user_roles = set(
        user.roles.filter(is_active=True).values_list("codename", flat=True),
    )
    return primary_role in allowed_roles or bool(user_roles & allowed_roles)


class IsEMISStaff(BasePermission):
    def has_permission(self, request, view):
        return _user_has_role(request.user, {EMIS_STAFF_ROLE})
