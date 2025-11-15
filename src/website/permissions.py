from rest_framework.permissions import BasePermission

from src.libs.permissions import validate_permissions, get_user_permissions
from rest_framework.permissions import SAFE_METHODS


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


class CampusEventPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_campus_event",
            "POST": "add_campus_event",
            "PATCH": "edit_campus_event",
            "DELETE": "delete_campus_event",
        }
        return validate_permissions(request, user_permissions_dict)


class CampusUnionPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_campus_union",
            "POST": "add_campus_union",
            "PATCH": "edit_campus_union",
            "DELETE": "delete_campus_union",
        }
        return validate_permissions(request, user_permissions_dict)


class CampusSectionPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_campus_section",
            "POST": "add_campus_section",
            "PATCH": "edit_campus_section",
            "DELETE": "delete_campus_section",
        }
        return validate_permissions(request, user_permissions_dict)


class CampusUnitPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_campus_unit",
            "POST": "add_campus_unit",
            "PATCH": "edit_campus_unit",
            "DELETE": "delete_campus_unit",
        }
        return validate_permissions(request, user_permissions_dict)


class ResearchFacilityPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_researchfacility",
            "POST": "add_researchfacility",
            "PATCH": "edit_researchfacility",
            "DELETE": "delete_researchfacility",
        }
        return validate_permissions(request, user_permissions_dict)


class StudentClubPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_student_club",
            "POST": "add_student_club",
            "PATCH": "edit_student_club",
            "DELETE": "delete_student_club",
        }
        return validate_permissions(request, user_permissions_dict)


class StudentClubEventPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_student_club_event",
            "POST": "add_student_club_event",
            "PATCH": "edit_student_club_event",
            "DELETE": "delete_student_club_event",
        }
        return validate_permissions(request, user_permissions_dict)


class GlobalGalleryPermission(BasePermission):
    SAFE_PERMISSIONS = {
        "view_campusevent",
        "view_studentclubevent",
        "view_departmentevent",
    }

    def has_permission(self, request, view):
        if request.user and request.user.is_superuser:
            return True

        if request.method not in SAFE_METHODS:
            return False

        user_permissions = get_user_permissions(request)
        user_codenames = {perm.codename for perm in user_permissions}
        return any(code in user_codenames for code in self.SAFE_PERMISSIONS)


class GlobalGalleryImagePermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_globalgalleryimage",
            "POST": "add_globalgalleryimage",
            "PATCH": "change_globalgalleryimage",
            "DELETE": "delete_globalgalleryimage",
        }

        return validate_permissions(request, user_permissions_dict)


class GlobalEventPermission(BasePermission):
    def has_permission(self, request, view):
        user_permissions_dict = {
            "SAFE_METHODS": "view_globalevent",
            "POST": "add_globalevent",
            "PATCH": "change_globalevent",
            "DELETE": "delete_globalevent",
        }

        return validate_permissions(request, user_permissions_dict)
