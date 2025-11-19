# ruff: noqa
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string

# Project Imports
from src.core.models import EmailConfig
from src.libs.loggers import email_logger as logger
import os
from django.conf import settings


def get_email_config(email_type: str):
    """Get Email Configs Based on mail type"""

    config = EmailConfig.objects.filter(email_type=email_type).first()

    if config:
        return {
            "EMAIL_HOST": config.email_host,
            "EMAIL_USE_TLS": config.email_use_tls,
            "EMAIL_USE_SSL": config.email_use_ssl,
            "EMAIL_PORT": config.email_port,
            "EMAIL_HOST_USER": config.email_host_user,
            "EMAIL_HOST_PASSWORD": config.email_host_password,
            "DEFAULT_FROM_EMAIL": config.default_from_email,
            "SERVER_EMAIL": config.server_mail,
        }

    logger.error("No email configuration found for email_type: %s", email_type)
    # Fallback to environment / Django settings if DB config is not present.
    # This allows configuring SMTP (e.g. Gmail) via environment variables.
    try:
        env_config = {
            "EMAIL_HOST": os.environ.get("EMAIL_HOST") or getattr(settings, "EMAIL_HOST", None),
            "EMAIL_USE_TLS": os.environ.get("EMAIL_USE_TLS", str(getattr(settings, "EMAIL_USE_TLS", False))).lower() in ("1", "true", "yes"),
            "EMAIL_USE_SSL": os.environ.get("EMAIL_USE_SSL", str(getattr(settings, "EMAIL_USE_SSL", False))).lower() in ("1", "true", "yes"),
            "EMAIL_PORT": int(os.environ.get("EMAIL_PORT") or getattr(settings, "EMAIL_PORT", 587)),
            "EMAIL_HOST_USER": os.environ.get("EMAIL_HOST_USER") or getattr(settings, "EMAIL_HOST_USER", None),
            "EMAIL_HOST_PASSWORD": os.environ.get("EMAIL_HOST_PASSWORD") or getattr(settings, "EMAIL_HOST_PASSWORD", None),
            "DEFAULT_FROM_EMAIL": os.environ.get("DEFAULT_FROM_EMAIL") or getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@localhost"),
            "SERVER_EMAIL": os.environ.get("SERVER_EMAIL") or getattr(settings, "SERVER_EMAIL", "server@localhost"),
        }

        # Ensure at least EMAIL_HOST and EMAIL_HOST_USER are present to attempt sending
        if env_config["EMAIL_HOST"] and env_config["EMAIL_HOST_USER"]:
            logger.info("Using environment email configuration for sending emails.")
            return env_config
    except Exception:
        logger.exception("Error while reading environment email configuration.")

    return None


def _send_email(
    subject,
    body,
    template_name,
    context,
    recipient_email,
    email_type="INFO",
):
    email_config = get_email_config(email_type=email_type)

    try:
        connection = get_connection(
            host=email_config["EMAIL_HOST"],
            port=email_config["EMAIL_PORT"],
            username=email_config["EMAIL_HOST_USER"],
            password=email_config["EMAIL_HOST_PASSWORD"],
            use_tls=email_config["EMAIL_USE_TLS"],
            use_ssl=email_config["EMAIL_USE_SSL"],
        )
    except (KeyError, Exception):
        logger.exception("Failed to make smtp connection.")

    email_template = render_to_string(f"{template_name}.html", context)
    mail = EmailMultiAlternatives(
        subject,
        body,
        from_email=email_config["DEFAULT_FROM_EMAIL"],
        to=[recipient_email],
        connection=connection,
    )

    if email_template:
        mail.attach_alternative(email_template, "text/html")

    try:
        mail.send(fail_silently=False)
    except Exception:
        logger.exception("Failed to send email to %s", recipient_email)
        return False

    return True
