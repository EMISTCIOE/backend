from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .auth_views import (
    UserChangePasswordView,
    UserLoginView,
    UserLogoutView,
    UserProfileUpdateView,
    UserProfileView,
    UserTokenRefreshView,
    UserVerifyAccountAPIView,
)
from .listing_apis.views import RoleForUserView
from .views import RoleArchiveView, RoleViewSet, UserArchiveView, UserViewSet

router = DefaultRouter(trailing_slash=False)

router.register("users", UserViewSet, basename="users")
router.register("roles", RoleViewSet, basename="roles")

urlpatterns = [
    # User Auth
    # ---------------------------------------------------------------------------------
    path("auth/login", UserLoginView.as_view(), name="user-login"),
    path("auth/logout", UserLogoutView.as_view(), name="user-logout"),
    path("auth/token/refresh", UserTokenRefreshView.as_view(), name="token-refresh"),
    path(
        "auth/verify",
        UserVerifyAccountAPIView.as_view(),
        name="verify-account",
    ),
    path("account/profile", UserProfileView.as_view(), name="user-profile"),
    path(
        "account/profile/update",
        UserProfileUpdateView.as_view(),
        name="user-profile-update",
    ),
    path(
        "account/change-password",
        UserChangePasswordView.as_view(),
        name="user-change-password",
    ),
    # User/Roles Setup
    # ----------------------------------------------------------------------------------
    path(
        "roles/<int:role_id>/archive",
        RoleArchiveView.as_view(),
        name="user-role-archive",
    ),
    path("users/<int:user_id>/archive", UserArchiveView.as_view(), name="user-archive"),
    # Listing APIs
    # ----------------------------------------------------------------------------------
    path("users/roles", RoleForUserView.as_view(), name="user-roles"),
    path("", include(router.urls)),
]
