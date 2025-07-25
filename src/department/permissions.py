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


class AcademicProgramPermission(BasePermission):
    def has_permission(self, request, view):
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


class DepartmentEventPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_department_event",
            "POST": "add_department_event",
            "PATCH": "edit_department_event",
            "DELETE": "delete_department_event",
        }
        return validate_permissions(request, user_permissions_dict)


class DepartmentPlanAndPolicyPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_department_planandpolicy",
            "POST": "add_department_planandpolicy",
            "PATCH": "edit_department_planandpolicy",
            "DELETE": "delete_department_planandpolicy",
        }
        return validate_permissions(request, user_permissions_dict)


class StaffMemberPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_staff_member",
            "POST": "add_staff_member",
            "PATCH": "edit_staff_member",
            "DELETE": "delete_staff_member",
        }
        return validate_permissions(request, user_permissions_dict)
