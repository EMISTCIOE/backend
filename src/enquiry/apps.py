"""
Enquiry App Configuration
"""

from django.apps import AppConfig


class EnquiryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src.enquiry"
    verbose_name = "Enquiry Management"
