from rest_framework.permissions import SAFE_METHODS

from src.user.models import User


def _get_user_role_codenames(user: User, module: str) -> set[str]:
    """
    Anonymous user  -> empty set
    Normal user     -> every codename of roles assigned to that user
    """
    if user.is_anonymous:
        return set()

    if module == "CMS":
        return set(
            user.roles.filter(is_cms_role=True).values_list("codename", flat=True)
        )
    else:
        return set(
            user.roles.filter(is_cms_role=False).values_list("codename", flat=True)
        )


def validate_permissions(
    request,
    role_method_map: dict[str, list[str]],
    module="CMS",
) -> bool:
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

    user_roles = _get_user_role_codenames(user, module)

    method_key = "SAFE_METHODS" if request.method in SAFE_METHODS else request.method
    allowed_roles = set(role_method_map.get(method_key, []))
    if not allowed_roles:
        return False

    return bool(user_roles & allowed_roles)
