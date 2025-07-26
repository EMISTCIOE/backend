from rest_framework.permissions import BasePermission

from src.libs.permissions import validate_permissions


class CampusReportPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_campus_report",
            "POST": "add_campus_report",
            "PATCH": "edit_campus_report",
            "DELETE": "delete_campus_report",
        }
        return validate_permissions(request, user_permissions_dict)


class CampusEventPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_campus_event",
            "POST": "add_campus_event",
            "PATCH": "edit_campus_event",
            "DELETE": "delete_campus_event",
        }
        return validate_permissions(request, user_permissions_dict)


class CampusInfoPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_campus_info",
            "POST": "add_campus_info",
            "PATCH": "edit_campus_info",
            "DELETE": "delete_campus_info",
        }

        return validate_permissions(request, user_permissions_dict)


class CampusKeyOfficialPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_campus_key_official",
            "POST": "add_campus_key_official",
            "PATCH": "edit_campus_key_official",
            "DELETE": "delete_campus_key_official",
        }

        return validate_permissions(request, user_permissions_dict)


class CampusFeedbackPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_campus_feedback",
            "POST": "add_campus_feedback",
            "PATCH": "edit_campus_feedback",
            "DELETE": "delete_campus_feedback",
        }
        return validate_permissions(request, user_permissions_dict)


class CampusDownloadPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_campus_download",
            "POST": "add_campus_download",
            "PATCH": "edit_campus_download",
            "DELETE": "delete_campus_download",
        }
        return validate_permissions(request, user_permissions_dict)


class CampusReportPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_campusreport",
            "POST": "add_campusreport",
            "PATCH": "edit_campusreport",
            "DELETE": "delete_campusreport",
        }
        return validate_permissions(request, user_permissions_dict)


class AcademicCalendarPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_academic_calendar",
            "POST": "add_academic_calendar",
            "PATCH": "edit_academic_calendar",
            "DELETE": "delete_academic_calendar",
        }
        return validate_permissions(request, user_permissions_dict)