from rest_framework.permissions import SAFE_METHODS

from src.user.constants import EMIS_STAFF_ROLE


def get_user_permissions(request):
    user_permissions = []

    user = request.user
    if user.is_anonymous:
        return user_permissions

    return user.get_all_permissions()


def user_has_roles(user, allowed_roles: set[str]) -> bool:
    """
    Check whether the user has any of the given roles, considering both the
    primary role field and any active roles assigned via the M2M `roles`.
    """
    if not user or user.is_anonymous:
        return False

    if getattr(user, "is_superuser", False):
        return True

    primary_role = getattr(user, "role", None)
    if primary_role in allowed_roles:
        return True

    if hasattr(user, "roles"):
        return user.roles.filter(is_active=True, codename__in=allowed_roles).exists()

    return False


def validate_permissions(request, user_permissions_dict):
    if request.user.is_anonymous:
        return False

    if not request.user.is_active:
        return False

    # EMIS staff should have blanket access across CMS/backends
    if user_has_roles(request.user, {EMIS_STAFF_ROLE}):
        return True

    if request.user.is_superuser:
        return True

    method = request.method
    if method in SAFE_METHODS:
        method = "SAFE_METHODS"

    user_permissions = get_user_permissions(request)
    required_permission = user_permissions_dict.get(method)

    codename_list = [perm.codename for perm in user_permissions]
    if required_permission and required_permission in codename_list:
        return True

    return False
