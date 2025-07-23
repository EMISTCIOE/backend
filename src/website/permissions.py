from rest_framework.permissions import BasePermission

class CampusInfoPermission(BasePermission):
    """
    Allow only staff to use this API.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff

