from rest_framework.permissions import SAFE_METHODS


def _get_user_role_codenames(user) -> set[str]:
    """
    Anonymous user  -> empty set
    Normal user     -> every codename of roles assigned to that user
    """
    if user.is_anonymous:
        return set()
    return set(user.roles.values_list("codename", flat=True))


def validate_permissions(request, role_method_map: dict[str, list[str]]) -> bool:
    """
    role_method_map must look like:

        {
            "SAFE_METHODS": ["viewer", "editor", "admin"],
            "POST":         ["admin"],
            "PATCH":        ["editor", "admin"],
            "DELETE":       ["admin"],
        }

    • If the current user has ANY role codename listed for the current
      HTTP method (or SAFE_METHODS for GET/HEAD/OPTIONS), access is granted.
    • Superusers can always pass.
    """
    user = request.user

    if user.is_anonymous or not user.is_active:
        return False
    if user.is_superuser:
        return True

    method_key = "SAFE_METHODS" if request.method in SAFE_METHODS else request.method
    allowed_roles = set(role_method_map.get(method_key, []))
    if not allowed_roles:
        return False

    user_roles = _get_user_role_codenames(user)
    return bool(user_roles & allowed_roles)
