from rest_framework.permissions import BasePermission

from src.libs.permissions import validate_permissions, user_has_roles
from src.user.constants import ADMIN_ROLE, EMIS_STAFF_ROLE


class UserSetupPermission(BasePermission):
    def has_permission(self, request, view):
        # Allow Admin and EMIS staff role-based access
        if user_has_roles(request.user, {ADMIN_ROLE, EMIS_STAFF_ROLE}):
            return True
            
        user_permissions_dict = {
            "SAFE_METHODS": "view_user",
            "POST": "add_user",
            "PATCH": "edit_user",
            "DELETE": "delete_user",
        }

        return validate_permissions(request, user_permissions_dict)


class RoleSetupPermission(BasePermission):
    def has_permission(self, request, view):
        # Allow Admin and EMIS staff role-based access
        if user_has_roles(request.user, {ADMIN_ROLE, EMIS_STAFF_ROLE}):
            return True
            
        user_permissions_dict = {
            "SAFE_METHODS": "view_user_role",
            "POST": "add_user_role",
            "PATCH": "edit_user_role",
            "DELETE": "delete_user_role",
        }

        return validate_permissions(request, user_permissions_dict)


class IsEMISStaff(BasePermission):
    def has_permission(self, request, view):
        return user_has_roles(request.user, {EMIS_STAFF_ROLE})
