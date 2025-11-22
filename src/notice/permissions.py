from rest_framework.permissions import BasePermission, SAFE_METHODS

from src.libs.permissions import validate_permissions, user_has_roles
from src.user.constants import (
    UNION_ROLE,
    CAMPUS_UNIT_ROLE,
    CAMPUS_SECTION_ROLE,
    ADMIN_ROLE,
    EMIS_STAFF_ROLE,
    DEPARTMENT_ADMIN_ROLE,
    CLUB_ROLE,
)


class NoticePermission(BasePermission):
    def has_permission(self, request, view):
        # Allow Admin and EMIS staff role-based access
        if user_has_roles(request.user, {ADMIN_ROLE, EMIS_STAFF_ROLE}):
            return True
            
        # Block Union users from notice operations (except viewing)
        if user_has_roles(request.user, {UNION_ROLE}):
            return request.method in SAFE_METHODS
        
        # Allow scoped roles basic notice access (view/create/update) within CMS
        if user_has_roles(
            request.user,
            {
                CAMPUS_UNIT_ROLE,
                CAMPUS_SECTION_ROLE,
                DEPARTMENT_ADMIN_ROLE,
                CLUB_ROLE,
            },
        ):
            return True

        user_permissions_dict = {
            "SAFE_METHODS": "view_notice",
            "POST": "add_notice",
            "PATCH": "change_notice",
            "DELETE": "delete_notice",
        }

        return validate_permissions(request, user_permissions_dict)
    
    def has_object_permission(self, request, view, obj):
        # Allow Admin and EMIS staff role-based access
        if user_has_roles(request.user, {ADMIN_ROLE, EMIS_STAFF_ROLE}):
            return True
            
        # Union users can only read notices
        if user_has_roles(request.user, {UNION_ROLE}):
            return request.method in SAFE_METHODS
        
        # Unit users can only access notices linked to their unit
        if user_has_roles(request.user, {CAMPUS_UNIT_ROLE}):
            unit_id = getattr(request.user, 'campus_unit_id', None)
            if unit_id:
                return obj.campus_unit_id == unit_id
            return False
        
        # Section users can only access notices linked to their section
        if user_has_roles(request.user, {CAMPUS_SECTION_ROLE}):
            section_id = getattr(request.user, 'campus_section_id', None)
            if section_id:
                return obj.campus_section_id == section_id
            return False
        
        # Department admins can access notices in their department (needed for approval toggles)
        if user_has_roles(request.user, {DEPARTMENT_ADMIN_ROLE}):
            department_id = getattr(request.user, 'department_id', None)
            if not department_id:
                return False

            # Direct department link
            if obj.department_id and str(obj.department_id) == str(department_id):
                return True

            # Fallback: allow if the creator belongs to the same department (helps when department field is missing)
            created_by_dept = getattr(getattr(obj, "created_by", None), "department_id", None)
            if created_by_dept and str(created_by_dept) == str(department_id):
                return True

            # Allow the creator themselves to manage (if still department admin)
            if getattr(obj, "created_by_id", None) and obj.created_by_id == getattr(request.user, "id", None):
                return True

            return False

        # Club users can only access notices linked to their department (club notices flow)
        if user_has_roles(request.user, {CLUB_ROLE}):
            department_id = getattr(request.user, 'department_id', None)
            if department_id:
                return obj.department_id == department_id
            return False
        
        # Other roles: check standard permissions
        user_permissions_dict = {
            "SAFE_METHODS": "view_notice",
            "POST": "add_notice",
            "PATCH": "change_notice",
            "DELETE": "delete_notice",
        }
        return validate_permissions(request, user_permissions_dict)


class NoticeStatusUpdatePermission(BasePermission):
    """Permission class specifically for notice status updates."""

    def has_permission(self, request, view):
        # Only allow Admin, EMIS Staff, and Department Admin to update notice status
        if user_has_roles(request.user, {ADMIN_ROLE, EMIS_STAFF_ROLE, DEPARTMENT_ADMIN_ROLE}):
            return True
        
        # Block Campus Unit and Section users from updating status
        if hasattr(request.user, 'role') and request.user.role in {CAMPUS_UNIT_ROLE, CAMPUS_SECTION_ROLE}:
            return False

        user_permissions_dict = {
            "PATCH": "edit_notice_status",
        }

        return validate_permissions(request, user_permissions_dict)

    def has_object_permission(self, request, view, obj):
        # Admin and EMIS staff can change any notice status
        if user_has_roles(request.user, {ADMIN_ROLE, EMIS_STAFF_ROLE}):
            return True

        # Department admins can change status for notices in their department (or created by them)
        if getattr(request.user, "role", None) == DEPARTMENT_ADMIN_ROLE:
            department_id = getattr(request.user, "department_id", None)
            if not department_id:
                return False

            if obj.department_id and str(obj.department_id) == str(department_id):
                return True

            created_by_dept = getattr(getattr(obj, "created_by", None), "department_id", None)
            if created_by_dept and str(created_by_dept) == str(department_id):
                return True

            if getattr(obj, "created_by_id", None) == getattr(request.user, "id", None):
                return True

            return False

        return False
