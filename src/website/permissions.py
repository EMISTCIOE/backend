from rest_framework.permissions import SAFE_METHODS, BasePermission

from src.libs.permissions import get_user_permissions, validate_permissions


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
        # Union users can view and edit their own union
        if getattr(request.user, 'role', None) == 'UNION':
            if request.method in SAFE_METHODS or request.method == 'PATCH':
                return True
            # Union users cannot create or delete unions
            return False
        
        user_permissions_dict = {
            "SAFE_METHODS": "view_campus_union",
            "POST": "add_campus_union",
            "PATCH": "edit_campus_union",
            "DELETE": "delete_campus_union",
        }
        return validate_permissions(request, user_permissions_dict)
    
    def has_object_permission(self, request, view, obj):
        # Union users can only access their own union
        if getattr(request.user, 'role', None) == 'UNION':
            if getattr(request.user, 'union_id', None):
                return str(obj.id) == str(request.user.union_id)
            return False
        
        # Other roles already validated at the permission level
        return True


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
        if getattr(request.user, "role", None) == "UNION":
            if request.method in SAFE_METHODS or request.method in {"POST", "PATCH", "DELETE"}:
                return True
            return False

        user_permissions_dict = {
            "SAFE_METHODS": "view_globalgalleryimage",
            "POST": "add_globalgalleryimage",
            "PATCH": "change_globalgalleryimage",
            "DELETE": "delete_globalgalleryimage",
        }

        return validate_permissions(request, user_permissions_dict)

    def has_object_permission(self, request, view, obj):
        if getattr(request.user, "role", None) == "UNION":
            union_id = getattr(request.user, "union_id", None)
            if not union_id:
                return False

            if obj.union_id:
                return str(obj.union_id) == str(union_id)

            if obj.global_event_id:
                return obj.global_event.unions.filter(id=union_id).exists()

            return False

        return True


class GlobalEventPermission(BasePermission):
    def has_permission(self, request, view):
        # Union users can create and edit global events (for their union)
        if hasattr(request.user, 'role') and request.user.role == 'UNION':
            if request.method in SAFE_METHODS or request.method in ['POST', 'PATCH']:
                return True
            # Union users cannot delete global events
            return False
        
        # Department users can create and edit global events (for their department and clubs)
        if hasattr(request.user, 'role') and request.user.role == 'DEPARTMENT':
            if request.method in SAFE_METHODS or request.method in ['POST', 'PATCH']:
                return True
            # Department users cannot delete global events
            return False
        
        # Club users can create and edit global events (for their club)
        if hasattr(request.user, 'role') and request.user.role == 'CLUB':
            if request.method in SAFE_METHODS or request.method in ['POST', 'PATCH']:
                return True
            # Club users cannot delete global events
            return False
        
        user_permissions_dict = {
            "SAFE_METHODS": "view_globalevent",
            "POST": "add_globalevent",
            "PATCH": "change_globalevent",
            "DELETE": "delete_globalevent",
        }

        return validate_permissions(request, user_permissions_dict)
    
    def has_object_permission(self, request, view, obj):
        # Union users can only access events linked to their union
        if hasattr(request.user, 'role') and request.user.role == 'UNION':
            if hasattr(request.user, 'union') and request.user.union:
                # Check if the event is linked to the user's union
                return obj.unions.filter(id=request.user.union.id).exists()
            return False
        
        # Department users can access events linked to their department or their department's clubs
        if hasattr(request.user, 'role') and request.user.role == 'DEPARTMENT':
            if hasattr(request.user, 'department') and request.user.department:
                # Check if the event is linked to the user's department or department's clubs
                department_linked = obj.departments.filter(id=request.user.department.id).exists()
                # Check if the event is linked to any club under this department
                department_clubs_linked = obj.clubs.filter(department=request.user.department).exists()
                return department_linked or department_clubs_linked
            return False
        
        # Club users can only access events linked to their club
        if hasattr(request.user, 'role') and request.user.role == 'CLUB':
            if hasattr(request.user, 'club') and request.user.club:
                # Check if the event is linked to the user's club
                return obj.clubs.filter(id=request.user.club.id).exists()
            return False
        
        # Other roles: check standard permissions
        user_permissions_dict = {
            "SAFE_METHODS": "view_globalevent",
            "POST": "add_globalevent",
            "PATCH": "change_globalevent",
            "DELETE": "delete_globalevent",
        }
        return validate_permissions(request, user_permissions_dict)
