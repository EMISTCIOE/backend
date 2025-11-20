from datetime import datetime

import pytz
from django.templatetags.static import static
from rest_framework import serializers

from src.libs.messages import UNKNOWN_ERROR
from src.libs.send_mail import _send_email, send_welcome_email as _send_welcome_email, send_password_reset_email as _send_password_reset_email
from src.user.models import User


def _build_origin_url(request):
    origin_url = request.headers.get("origin")
    if not origin_url:
        origin_url = request.build_absolute_uri("/")
    return origin_url.rstrip("/")


def _timestamp_info():
    now_kathmandu = datetime.now(pytz.timezone("Asia/Kathmandu"))
    return (
        now_kathmandu.strftime("%B %d, %Y at %I:%M %p %Z"),
        now_kathmandu.year,
    )


def _user_identity_snapshot(user: User):
    """Return primary role and designation metadata for emails."""

    primary_role_label = getattr(user, "get_role_display", None)
    primary_role_label = primary_role_label() if callable(primary_role_label) else None
    if not primary_role_label:
        primary_role_label = getattr(user, "role", "")

    designation_obj = getattr(user, "designation", None)
    designation_title = getattr(designation_obj, "title", None)

    role_names = list(
        user.roles.filter(is_active=True).values_list("name", flat=True),
    )
    secondary_roles = ", ".join(role_names)

    return primary_role_label, designation_title, secondary_roles


def send_user_forget_password_email(
    recipient_email: str,
    user: User,
    token: str,
    request,
    redirect_url: str = "reset-password",
):
    """
    Send password reset email to user.
    Enhanced to use the improved send_password_reset_email function.
    """
    try:
        origin_url = _build_origin_url(request)
        reset_link = f"{origin_url}/{redirect_url}/{token}"
        
        # Use the enhanced password reset email function
        success = _send_password_reset_email(
            user=user,
            reset_link=reset_link,
            request=request
        )
        
        if not success:
            raise Exception("Failed to send password reset email")
            
    except Exception as err:
        raise serializers.ValidationError({"error": UNKNOWN_ERROR}) from err


def send_user_account_verification_email(
    recipient_email: str,
    token: str,
    request,
    redirect_url: str = "verify-account",
):
    origin_url = _build_origin_url(request)

    try:
        subject = "Account Verification"
        body = "Please verify your account using the provided link"
        email_template_name = "user/account-verification"
        verification_url = f"{origin_url}/{redirect_url}/{token}"
        logo_url = request.build_absolute_uri(static("images/logo.png"))

        email_context = {
            "verification_url": verification_url,
            "logo": logo_url,
            "username": "User",
        }

        _send_email(
            subject,
            body,
            email_template_name,
            email_context,
            recipient_email,
        )
    except Exception as err:
        raise serializers.ValidationError({"error": UNKNOWN_ERROR}) from err


def send_user_welcome_email(
    user: User,
    password: str,
    request,
    login_url: str | None = None,
    privileges: list[str] | None = None,
):
    """
    Send welcome email to newly created user.
    Enhanced to use the improved send_welcome_email function.
    """
    try:
        # Use the enhanced welcome email function
        success = _send_welcome_email(
            user=user,
            password=password,
            request=request,
            login_url=login_url,
            privileges=privileges
        )
        
        if not success:
            raise Exception("Failed to send welcome email")
            
    except Exception as err:
        raise serializers.ValidationError({"error": UNKNOWN_ERROR}) from err
