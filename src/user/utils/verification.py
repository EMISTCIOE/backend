from rest_framework import serializers
from django.templatetags.static import static

from src.libs.messages import UNKNOWN_ERROR
from src.libs.send_mail import _send_email


def send_user_forget_password_email(
    recipient_email: str,
    token: str,
    request,
    redirect_url: str = "reset-password",
):
    origin_url = request.headers.get("origin")

    try:
        subject = "Forget Password"
        body = "Account Information"
        email_template_name = "user/forget-password"
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


def send_user_account_verification_email(
    recipient_email: str,
    token: str,
    request,
    redirect_url: str = "verify-account",
):
    origin_url = request.headers.get("origin")

    try:
        subject = "Account Verification"
        body = "Account Information"
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
