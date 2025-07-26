# ruff: noqa
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string

# Project Imports
from src.core.models import EmailConfig
from src.libs.loggers import email_logger as logger


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
