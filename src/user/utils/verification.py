from datetime import datetime

import pytz
from django.templatetags.static import static
from rest_framework import serializers

from src.libs.messages import UNKNOWN_ERROR
from src.libs.send_mail import _send_email
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


def send_user_forget_password_email(
    recipient_email: str,
    user: User,
    token: str,
    request,
    redirect_url: str = "reset-password",
):
    origin_url = _build_origin_url(request)

    try:
        subject = "Reset Your TCIOE EMIS Password"
        reset_link = f"{origin_url}/{redirect_url}/{token}"
        body = f"Use this link to reset your password: {reset_link}"
        email_template_name = "emails/password_reset"
        logo_url = request.build_absolute_uri(static("images/logo.png"))
        sent_time, current_year = _timestamp_info()
        user_name = user.get_full_name() or user.username
        role_names = user.roles.filter(is_active=True).values_list("name", flat=True)
        user_role = ", ".join(role_names) if role_names else ""  # noqa: E501

        email_context = {
            "user": user,
            "user_name": user_name,
            "username": user.username,
            "user_email": user.email,
            "user_role": user_role,
            "reset_link": reset_link,
            "logo": logo_url,
            "current_year": current_year,
            "sent_time": sent_time,
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
    origin_url = _build_origin_url(request)

    try:
        subject = "Welcome to TCIOE EMIS"
        email_template_name = "emails/welcome_user"
        body = "Welcome to TCIOE EMIS. Your account credentials are attached."
        logo_url = request.build_absolute_uri(static("images/logo.png"))
        sent_time, current_year = _timestamp_info()
        user_name = user.get_full_name() or user.username
        role_names = user.roles.filter(is_active=True).values_list("name", flat=True)
        user_role = ", ".join(role_names) if role_names else ""
        contact_number = getattr(user, "phone_no", None)
        resolved_login_url = login_url or f"{origin_url}/login"
        default_privileges = [
            "Access the internal TCIOE EMIS dashboards",
            "Track enquiries and notices",
            "Coordinate department workflows",
        ]
        email_privileges = privileges or default_privileges

        email_context = {
            "user": user,
            "user_name": user_name,
            "username": user.username,
            "user_email": user.email,
            "password": password,
            "user_role": user_role,
            "contact_number": contact_number,
            "login_url": resolved_login_url,
            "logo": logo_url,
            "privileges": email_privileges,
            "current_year": current_year,
            "sent_time": sent_time,
        }

        _send_email(
            subject,
            body,
            email_template_name,
            email_context,
            user.email,
        )
    except Exception as err:
        raise serializers.ValidationError({"error": UNKNOWN_ERROR}) from err
