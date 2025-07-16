from django.contrib.sites.shortcuts import get_current_site
from django.templatetags.static import static
from rest_framework import serializers

# Project Imports
from src.libs.messages import UNKNOWN_ERROR
from src.libs.send_mail import _send_email, get_basic_urls
from src.libs.loggers import email_logger as logger


def send_user_account_verification_email(
    recipient_email: str,
    token: str,
    request,
    redirect_url="verify-account",
):
    current_site = get_current_site(request)
    lock_url = f'https://{current_site.domain}{static("images/icons/lock.png")}'
    origin_url = request.headers.get("origin", "")

    try:
        subject = "Account Verification"
        body = "Account Information"
        email_template_name = "user/account_verification"
        verification_url = f"{origin_url}/{redirect_url}/{token}"

        email_context = {
            "token": token,
            "lock_url": lock_url,
            "basic_urls": get_basic_urls(request),
            "redirect_url": verification_url,
        }
        _send_email(
            subject,
            body,
            email_template_name,
            email_context,
            recipient_email,
        )

    except Exception as err:
        logger.error("Email not sent: %s", err)
        raise serializers.ValidationError({"error": UNKNOWN_ERROR}) from err
