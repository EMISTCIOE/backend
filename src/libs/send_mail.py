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
    """
    Enhanced email sending function with better error handling and logging.
    Inspired by tcioe-schedule implementation patterns.
    """
    # Validate inputs
    if not recipient_email:
        logger.error("Cannot send email: recipient_email is required")
        return False
    
    if not subject:
        logger.error("Cannot send email: subject is required")
        return False

    email_config = get_email_config(email_type=email_type)
    
    if not email_config:
        logger.error("Cannot send email: No email configuration available")
        return False

    try:
        connection = get_connection(
            host=email_config["EMAIL_HOST"],
            port=email_config["EMAIL_PORT"],
            username=email_config["EMAIL_HOST_USER"],
            password=email_config["EMAIL_HOST_PASSWORD"],
            use_tls=email_config["EMAIL_USE_TLS"],
            use_ssl=email_config["EMAIL_USE_SSL"],
            fail_silently=False,
        )
        
        # Test connection
        connection.open()
        logger.info("SMTP connection established successfully")
        
    except (KeyError, TypeError) as e:
        logger.error("Email configuration error: %s", str(e))
        return False
    except Exception as e:
        logger.error("Failed to establish SMTP connection: %s", str(e))
        logger.error("Email settings - Host: %s, Port: %s, User: %s", 
                    email_config.get("EMAIL_HOST", "Not set"),
                    email_config.get("EMAIL_PORT", "Not set"),
                    email_config.get("EMAIL_HOST_USER", "Not set"))
        return False

    try:
        # Render HTML template if template_name is provided
        html_message = None
        if template_name:
            try:
                html_message = render_to_string(f"{template_name}.html", context)
                logger.info("Email template rendered successfully: %s.html", template_name)
            except Exception as e:
                logger.warning("Failed to render email template %s.html: %s", template_name, str(e))
                # Continue without HTML template
        
        # Create email message
        mail = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=email_config["DEFAULT_FROM_EMAIL"],
            to=[recipient_email],
            connection=connection,
        )

        # Attach HTML alternative if available
        if html_message:
            mail.attach_alternative(html_message, "text/html")

        # Send email
        mail.send(fail_silently=False)
        logger.info("Email sent successfully to %s with subject: %s", recipient_email, subject)
        return True
        
    except Exception as e:
        logger.error("Failed to send email to %s: %s", recipient_email, str(e))
        logger.error("Email details - Subject: %s, Template: %s", subject, template_name)
        return False
    
    finally:
        try:
            connection.close()
        except Exception:
            pass  # Ignore connection close errors


def send_welcome_email(user, password=None, request=None, login_url=None, privileges=None):
    """
    Send welcome email to newly created user.
    Enhanced version matching tcioe-schedule patterns.
    """
    try:
        from datetime import datetime
        import pytz
        from django.templatetags.static import static
        
        # Get current timestamp in Nepal timezone
        nepal_tz = pytz.timezone('Asia/Kathmandu')
        current_time = datetime.now(nepal_tz)

        # Build login URL
        if request and not login_url:
            origin_url = f"{request.scheme}://{request.get_host()}"
            login_url = f"{origin_url}/login"
        elif not login_url:
            login_url = "https://app.tcioe.edu.np/"
        
        # Get user details
        user_name = user.get_full_name() or user.username
        user_type_display = getattr(user, 'get_user_type_display', lambda: 'User')()
        contact_number = getattr(user, 'phone_no', None) or getattr(user, 'contact_number', None)
        
        # Get logo URL
        logo_url = None
        if request:
            try:
                logo_url = request.build_absolute_uri(static("images/logo.png"))
            except Exception:
                pass

        # Prepare template context
        context = {
            'user_name': user_name,
            'user_email': user.email,
            'username': user.username,
            'user_type_display': user_type_display,
            'contact_number': contact_number,
            'password': password or 'Please contact admin for password',
            'login_url': login_url,
            'current_year': current_time.year,
            'sent_time': current_time.strftime('%B %d, %Y at %I:%M %p'),
            'logo': logo_url,
            'privileges': privileges or [
                'Access the internal TCIOE EMIS dashboards',
                'Track enquiries and notices', 
                'Coordinate department workflows'
            ]
        }

        # Send email
        subject = f'Welcome to TCIOE EMIS - {user_name}'
        body = f'Welcome to TCIOE EMIS, {user_name}. Your account has been created successfully.'
        
        return _send_email(
            subject=subject,
            body=body,
            template_name='emails/welcome_user',
            context=context,
            recipient_email=user.email,
            email_type="INFO"
        )
        
    except Exception as e:
        logger.error("Failed to send welcome email to %s: %s", user.email if user else "unknown", str(e))
        return False


def send_password_reset_email(user, reset_link, request=None):
    """
    Send password reset email to user.
    Enhanced version matching tcioe-schedule patterns.
    """
    try:
        from datetime import datetime
        import pytz
        from django.templatetags.static import static
        
        # Get current timestamp in Nepal timezone
        nepal_tz = pytz.timezone('Asia/Kathmandu')
        current_time = datetime.now(nepal_tz)
        
        # Get user details
        user_name = user.get_full_name() or user.username
        user_type_display = getattr(user, 'get_user_type_display', lambda: 'User')()
        
        # Get logo URL
        logo_url = None
        if request:
            try:
                logo_url = request.build_absolute_uri(static("images/logo.png"))
            except Exception:
                pass

        # Prepare template context
        context = {
            'user_name': user_name,
            'user_email': user.email,
            'username': user.username,
            'user_type_display': user_type_display,
            'reset_link': reset_link,
            'current_year': current_time.year,
            'sent_time': current_time.strftime('%B %d, %Y at %I:%M %p'),
            'sent_time_iso': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'logo': logo_url,
        }

        # Send email
        subject = f'Password Reset Request - {user_name}'
        body = f'Password reset instructions have been sent to {user.email}. Please check your email.'
        
        return _send_email(
            subject=subject,
            body=body,
            template_name='emails/password_reset',
            context=context,
            recipient_email=user.email,
            email_type="INFO"
        )
        
    except Exception as e:
        logger.error("Failed to send password reset email to %s: %s", user.email if user else "unknown", str(e))
        return False


def send_email_reset_received_notification(full_name, college_email, secondary_email, request_sequence, submitted_at, request=None):
    """
    Send notification email when email reset request is received.
    """
    try:
        from datetime import datetime
        import pytz
        from django.templatetags.static import static
        
        # Get current timestamp in Nepal timezone
        nepal_tz = pytz.timezone('Asia/Kathmandu')
        current_time = datetime.now(nepal_tz)
        
        # Get logo URL
        logo_url = None
        if request:
            try:
                logo_url = request.build_absolute_uri(static("images/logo.png"))
            except Exception:
                pass

        # Prepare template context
        context = {
            'full_name': full_name,
            'college_email': college_email,
            'secondary_email': secondary_email,
            'request_sequence': request_sequence,
            'submitted_at': submitted_at,
            'current_year': current_time.year,
            'logo': logo_url,
        }

        # Send email
        subject = 'Email Reset Request Received'
        body = f'Dear {full_name}, we have received your email reset request and will review it shortly.'
        
        return _send_email(
            subject=subject,
            body=body,
            template_name='emails/email_reset_received',
            context=context,
            recipient_email=secondary_email,
            email_type="INFO"
        )
        
    except Exception as e:
        logger.error("Failed to send email reset received notification to %s: %s", secondary_email, str(e))
        return False



