from rest_framework.permissions import SAFE_METHODS, BasePermission

from src.libs.permissions import validate_permissions
from src.user.constants import ADMIN_ROLE, EMIS_STAFF_ROLE, CAMPUS_UNIT_ROLE, CAMPUS_SECTION_ROLE


class DepartmentPermission(BasePermission):
    def has_permission(self, request, view):
        # Allow Admin and EMIS staff role-based access
        if hasattr(request.user, 'role') and request.user.role in {ADMIN_ROLE, EMIS_STAFF_ROLE}:
            return True
            
        # Allow campus unit and section users to view departments for form dropdowns
        if hasattr(request.user, 'role') and request.user.role in {CAMPUS_UNIT_ROLE, CAMPUS_SECTION_ROLE}:
            return request.method in SAFE_METHODS
            
        user_permissions_dict = {
            "SAFE_METHODS": "view_department",
            "POST": "add_department",
            "PATCH": "edit_department",
            "DELETE": "delete_department",
        }

        return validate_permissions(request, user_permissions_dict)


class AcademicProgramPermission(BasePermission):
    def has_permission(self, request, view):
        # Allow Admin and EMIS staff role-based access
        if hasattr(request.user, 'role') and request.user.role in {ADMIN_ROLE, EMIS_STAFF_ROLE}:
            return True

        # Allow campus unit and section users to view academic programs for form dropdowns
        if hasattr(request.user, 'role') and request.user.role in {CAMPUS_UNIT_ROLE, CAMPUS_SECTION_ROLE}:
            return request.method in SAFE_METHODS
            
        user_permissions_dict = {
            "SAFE_METHODS": "view_academic_program",
            "POST": "add_academic_program",
            "PATCH": "edit_academic_program",
            "DELETE": "delete_academic_program",
        }
        return validate_permissions(request, user_permissions_dict)


class DepartmentDownloadPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_department_download",
            "POST": "add_department_download",
            "PATCH": "edit_department_download",
            "DELETE": "delete_department_download",
        }
        return validate_permissions(request, user_permissions_dict)


class DepartmentPlanAndPolicyPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_department_plan_and_policy",
            "POST": "add_department_plan_and_policy",
            "PATCH": "edit_department_plan_and_policy",
            "DELETE": "delete_department_plan_and_policy",
        }
        return validate_permissions(request, user_permissions_dict)
