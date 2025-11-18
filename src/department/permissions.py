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


class DepartmentPlanAndPolicyPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_department_plan_and_policy",
            "POST": "add_department_plan_and_policy",
            "PATCH": "edit_department_plan_and_policy",
            "DELETE": "delete_department_plan_and_policy",
        }
        return validate_permissions(request, user_permissions_dict)
