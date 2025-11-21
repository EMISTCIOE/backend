from rest_framework.permissions import SAFE_METHODS, BasePermission

from src.libs.permissions import get_user_permissions, validate_permissions
from src.user.constants import (
    ADMIN_ROLE,
    CAMPUS_SECTION_ROLE,
    CAMPUS_UNIT_ROLE,
    CLUB_ROLE,
    DEPARTMENT_ADMIN_ROLE,
    EMIS_STAFF_ROLE,
    UNION_ROLE,
)


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
        # Allow Admin and EMIS staff role-based access
        if hasattr(request.user, 'role') and request.user.role in {ADMIN_ROLE, EMIS_STAFF_ROLE}:
            return True
            
        user_permissions_dict = {
            "SAFE_METHODS": "view_campus_key_official",
            "POST": "add_campus_key_official",
            "PATCH": "edit_campus_key_official",
            "DELETE": "delete_campus_key_official",
        }

        return validate_permissions(request, user_permissions_dict)


class CampusFeedbackPermission(BasePermission):
    def has_permission(self, request, view):
        # Allow Admin and EMIS staff role-based access
        if hasattr(request.user, 'role') and request.user.role in {ADMIN_ROLE, EMIS_STAFF_ROLE}:
            return True

        user_permissions_dict = {
            "SAFE_METHODS": "view_campus_feedback",
            "POST": "add_campus_feedback",
            "PATCH": "edit_campus_feedback",
            "DELETE": "delete_campus_feedback",
        }
        return validate_permissions(request, user_permissions_dict)


class CampusDownloadPermission(BasePermission):
    def has_permission(self, request, view):
        # Allow Admin and EMIS staff role-based access
        if hasattr(request.user, 'role') and request.user.role in {ADMIN_ROLE, EMIS_STAFF_ROLE}:
            return True

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
        # Union users can create, view and edit events for their union
        if getattr(request.user, 'role', None) == UNION_ROLE:
            if request.method in SAFE_METHODS or request.method in {'POST', 'PATCH', 'DELETE'}:
                return True
            return False
        
        user_permissions_dict = {
            "SAFE_METHODS": "view_campus_event",
            "POST": "add_campus_event",
            "PATCH": "edit_campus_event",
            "DELETE": "delete_campus_event",
        }
        return validate_permissions(request, user_permissions_dict)
    
    def has_object_permission(self, request, view, obj):
        # Union users can only access events for their own union
        if getattr(request.user, 'role', None) == UNION_ROLE:
            union_id = getattr(request.user, 'union_id', None)
            if not union_id:
                return False
            
            # Check if the event is associated with the user's union
            if hasattr(obj, 'unions') and obj.unions.filter(id=union_id).exists():
                return True
            # For older event models that might have a direct union field
            if hasattr(obj, 'union_id') and str(obj.union_id) == str(union_id):
                return True
            return False
        
        # Other roles already validated at the permission level
        return True


class CampusUnionPermission(BasePermission):
    def has_permission(self, request, view):
        # Allow Admin and EMIS staff role-based access
        if hasattr(request.user, 'role') and request.user.role in {ADMIN_ROLE, EMIS_STAFF_ROLE}:
            return True
            
        # Union users can view and edit their own union
        if getattr(request.user, 'role', None) == UNION_ROLE:
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
        if getattr(request.user, 'role', None) == UNION_ROLE:
            if getattr(request.user, 'union_id', None):
                return str(obj.id) == str(request.user.union_id)
            return False
        
        # Other roles already validated at the permission level
        return True


class CampusSectionPermission(BasePermission):
    def has_permission(self, request, view):
        # Allow Admin and EMIS staff role-based access
        if hasattr(request.user, 'role') and request.user.role in {ADMIN_ROLE, EMIS_STAFF_ROLE}:
            return True
            
        # Allow section users to manage their own section
        if getattr(request.user, "role", None) == CAMPUS_SECTION_ROLE:
            return request.method in SAFE_METHODS or request.method in {"PATCH"}
            
        # Allow campus unit users to view sections for notice form dropdowns
        if getattr(request.user, "role", None) == CAMPUS_UNIT_ROLE:
            return request.method in SAFE_METHODS

        user_permissions_dict = {
            "SAFE_METHODS": "view_campus_section",
            "POST": "add_campus_section",
            "PATCH": "edit_campus_section",
            "DELETE": "delete_campus_section",
        }
        return validate_permissions(request, user_permissions_dict)

    def has_object_permission(self, request, view, obj):
        if getattr(request.user, "role", None) == CAMPUS_SECTION_ROLE:
            return str(obj.id) == str(getattr(request.user, "campus_section_id", None))
        return True


class CampusUnitPermission(BasePermission):
    def has_permission(self, request, view):
        # Allow Admin and EMIS staff role-based access
        if hasattr(request.user, 'role') and request.user.role in {ADMIN_ROLE, EMIS_STAFF_ROLE}:
            return True
            
        # Allow unit users to manage their own unit
        if getattr(request.user, "role", None) == CAMPUS_UNIT_ROLE:
            return request.method in SAFE_METHODS or request.method in {"PATCH"}
            
        # Allow campus section users to view units for notice form dropdowns
        if getattr(request.user, "role", None) == CAMPUS_SECTION_ROLE:
            return request.method in SAFE_METHODS

        user_permissions_dict = {
            "SAFE_METHODS": "view_campus_unit",
            "POST": "add_campus_unit",
            "PATCH": "edit_campus_unit",
            "DELETE": "delete_campus_unit",
        }
        return validate_permissions(request, user_permissions_dict)

    def has_object_permission(self, request, view, obj):
        if getattr(request.user, "role", None) == CAMPUS_UNIT_ROLE:
            return str(obj.id) == str(getattr(request.user, "campus_unit_id", None))
        return True


class ResearchFacilityPermission(BasePermission):
    def has_permission(self, request, view):
        # Allow Admin and EMIS staff role-based access
        if hasattr(request.user, 'role') and request.user.role in {ADMIN_ROLE, EMIS_STAFF_ROLE}:
            return True

        user_permissions_dict = {
            "SAFE_METHODS": "view_researchfacility",
            "POST": "add_researchfacility",
            "PATCH": "edit_researchfacility",
            "DELETE": "delete_researchfacility",
        }
        return validate_permissions(request, user_permissions_dict)


class StudentClubPermission(BasePermission):
    def has_permission(self, request, view):
        # Allow Admin and EMIS staff role-based access
        if hasattr(request.user, 'role') and request.user.role in {ADMIN_ROLE, EMIS_STAFF_ROLE}:
            return True
            
        # Allow campus unit and section users to view student clubs for form dropdowns
        if hasattr(request.user, 'role') and request.user.role in {CAMPUS_UNIT_ROLE, CAMPUS_SECTION_ROLE}:
            return request.method in SAFE_METHODS
            
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

        # EMIS staff has full access to the global gallery
        if getattr(request.user, "role", None) == EMIS_STAFF_ROLE:
            return True

        # Allow scoped roles to view the global gallery
        if getattr(request.user, "role", None) in {
            UNION_ROLE,
            CAMPUS_UNIT_ROLE,
            CAMPUS_SECTION_ROLE,
            DEPARTMENT_ADMIN_ROLE,
            CLUB_ROLE,
        }:
            if request.method in SAFE_METHODS:
                return True
            return False

        if request.method not in SAFE_METHODS:
            return False

        user_permissions = get_user_permissions(request)
        user_codenames = {perm.codename for perm in user_permissions}
        return any(code in user_codenames for code in self.SAFE_PERMISSIONS)


class GlobalGalleryImagePermission(BasePermission):
    def has_permission(self, request, view):
        # EMIS staff has full access to gallery images
        if getattr(request.user, "role", None) == EMIS_STAFF_ROLE:
            return True

        if getattr(request.user, "role", None) in {
            UNION_ROLE,
            CAMPUS_UNIT_ROLE,
            CAMPUS_SECTION_ROLE,
            DEPARTMENT_ADMIN_ROLE,
            CLUB_ROLE,
        }:
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
        # EMIS staff can manage any gallery image
        if getattr(request.user, "role", None) == EMIS_STAFF_ROLE:
            return True

        if getattr(request.user, "role", None) in {
            UNION_ROLE,
            CAMPUS_UNIT_ROLE,
            CAMPUS_SECTION_ROLE,
            DEPARTMENT_ADMIN_ROLE,
            CLUB_ROLE,
        }:
            union_id = getattr(request.user, "union_id", None)
            unit_id = getattr(request.user, "campus_unit_id", None)
            section_id = getattr(request.user, "campus_section_id", None)
            department_id = getattr(request.user, "department_id", None)
            club_id = getattr(request.user, "club_id", None)

            # Union linkage
            if union_id:
                if obj.union_id and str(obj.union_id) == str(union_id):
                    return True
                if obj.global_event_id and obj.global_event.unions.filter(id=union_id).exists():
                    return True
            # Unit linkage
            if unit_id:
                if getattr(obj, "unit_id", None) and str(obj.unit_id) == str(unit_id):
                    return True
                if getattr(obj, "global_event_id", None) and obj.global_event and hasattr(obj.global_event, 'units') and obj.global_event.units.filter(id=unit_id).exists():
                    return True
            # Section linkage
            if section_id:
                if getattr(obj, "section_id", None) and str(obj.section_id) == str(section_id):
                    return True
                if getattr(obj, "global_event_id", None) and obj.global_event and hasattr(obj.global_event, 'sections') and obj.global_event.sections.filter(id=section_id).exists():
                    return True
            # Department linkage
            if department_id:
                if getattr(obj, "department_id", None) and str(obj.department_id) == str(department_id):
                    return True
                if getattr(obj, "global_event_id", None) and obj.global_event and hasattr(obj.global_event, "departments") and obj.global_event.departments.filter(id=department_id).exists():
                    return True
            # Club linkage
            if club_id:
                if getattr(obj, "club_id", None) and str(obj.club_id) == str(club_id):
                    return True
                if getattr(obj, "global_event_id", None) and obj.global_event and hasattr(obj.global_event, "clubs") and obj.global_event.clubs.filter(id=club_id).exists():
                    return True
            return False

        return True


class GlobalEventPermission(BasePermission):
    def _is_approval_only_update(self, request):
        """Check if the request is only updating approval fields"""
        if request.method != 'PATCH':
            return False
        
        data_keys = set(request.data.keys())
        approval_fields = {'is_approved_by_department', 'is_approved_by_campus'}
        
        # If only approval fields are being updated
        return data_keys.issubset(approval_fields) and len(data_keys) > 0
    
    def _can_change_approval_status(self, user):
        """Check if user can change approval status (admin and EMIS staff)"""
        return (
            user.is_superuser or 
            getattr(user, 'role', None) == ADMIN_ROLE or 
            getattr(user, 'role', None) == EMIS_STAFF_ROLE
        )
    
    def has_permission(self, request, view):
        # EMIS staff has full access to manage global events
        if getattr(request.user, "role", None) == EMIS_STAFF_ROLE:
            return True

        # Special case: Admin and EMIS staff can always change approval status
        if request.method == 'PATCH' and self._can_change_approval_status(request.user):
            if self._is_approval_only_update(request):
                return True
        
        # Union users can create and edit global events (for their union)
        if hasattr(request.user, 'role') and request.user.role == UNION_ROLE:
            if request.method in SAFE_METHODS or request.method in ['POST', 'PATCH']:
                return True
            # Union users cannot delete global events
            return False

        # Campus Unit/Section users can create and edit events for their own scope
        if hasattr(request.user, 'role') and request.user.role in {CAMPUS_UNIT_ROLE, CAMPUS_SECTION_ROLE}:
            if request.method in SAFE_METHODS or request.method in ['POST', 'PATCH']:
                return True
            return False
        
        # Department users can create and edit global events (for their department and clubs)
        if hasattr(request.user, 'role') and request.user.role == DEPARTMENT_ADMIN_ROLE:
            if request.method in SAFE_METHODS or request.method in ['POST', 'PATCH']:
                return True
            # Department users cannot delete global events
            return False
        
        # Club users can create and edit global events (for their club)
        if hasattr(request.user, 'role') and request.user.role == CLUB_ROLE:
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
        # EMIS staff can access any global event
        if getattr(request.user, "role", None) == EMIS_STAFF_ROLE:
            return True

        # Special case: Admin and EMIS staff can always change approval status for any event
        if request.method == 'PATCH' and self._can_change_approval_status(request.user):
            if self._is_approval_only_update(request):
                return True
        
        # Union users can only access events linked to their union
        if hasattr(request.user, 'role') and request.user.role == UNION_ROLE:
            union_id = getattr(request.user, 'union_id', None)
            if union_id:
                # Check if the event is linked to the user's union
                return obj.unions.filter(id=union_id).exists()
            return False

        # Unit/Section users can only access events linked to their scope
        if hasattr(request.user, 'role') and request.user.role in {CAMPUS_UNIT_ROLE, CAMPUS_SECTION_ROLE}:
            unit_id = getattr(request.user, 'campus_unit_id', None)
            section_id = getattr(request.user, 'campus_section_id', None)
            if unit_id and hasattr(obj, "units") and obj.units.filter(id=unit_id).exists():
                return True
            if section_id and hasattr(obj, "sections") and obj.sections.filter(id=section_id).exists():
                return True
            return False
        
        # Department users can access events linked to their department or their department's clubs
        if hasattr(request.user, 'role') and request.user.role == DEPARTMENT_ADMIN_ROLE:
            department_id = getattr(request.user, 'department_id', None)
            if department_id:
                # Check if the event is linked to the user's department or department's clubs
                department_linked = obj.departments.filter(id=department_id).exists()
                # Check if the event is linked to any club under this department
                department_clubs_linked = obj.clubs.filter(department_id=department_id).exists()
                return department_linked or department_clubs_linked
            return False
        
        # Club users can only access events linked to their club
        if hasattr(request.user, 'role') and request.user.role == CLUB_ROLE:
            club_id = getattr(request.user, 'club_id', None)
            if club_id:
                # Check if the event is linked to the user's club
                return obj.clubs.filter(id=club_id).exists()
            return False
        
        # Other roles: check standard permissions
        user_permissions_dict = {
            "SAFE_METHODS": "view_globalevent",
            "POST": "add_globalevent",
            "PATCH": "change_globalevent",
            "DELETE": "delete_globalevent",
        }
        return validate_permissions(request, user_permissions_dict)
