from django.db import models
from django.utils.translation import gettext_lazy as _

# Project Imports
from src.base.models import AuditInfoModel


class PhoneNumber(AuditInfoModel):
    """
    Phone Number model to store contact information for different departments and sections
    """
    
    department_name = models.CharField(
        _("Department/Section Name"), 
        max_length=100,
        help_text=_("Name of the department or section")
    )
    
    phone_number = models.CharField(
        _("Phone Number"), 
        max_length=20,
        help_text=_("Phone number for the department/section")
    )
    
    description = models.TextField(
        _("Description"), 
        blank=True, 
        null=True,
        help_text=_("Additional description or notes about this contact")
    )
    
    display_order = models.PositiveIntegerField(
        _("Display Order"),
        default=0,
        help_text=_("Order in which to display this phone number (lower numbers first)")
    )

    def __str__(self):
        return f"{self.department_name} - {self.phone_number}"

    class Meta:
        ordering = ['display_order', 'department_name']
        verbose_name = _("Phone Number")
        verbose_name_plural = _("Phone Numbers")