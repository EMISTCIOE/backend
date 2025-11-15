from django.db import models
from django.utils.translation import gettext_lazy as _

# Project Imports
from src.base.models import AuditInfoModel


class ContactType(models.TextChoices):
    """Types of contacts in the phone directory"""
    CAMPUS = 'campus', _('Campus')
    DEPARTMENT = 'department', _('Department')
    SECTION = 'section', _('Section/Unit')


class PhoneNumber(AuditInfoModel):
    """
    Phone Number model to store contact information for different departments and sections.
    Can be linked to a Department or represent a standalone unit/section/campus contact.
    """
    
    contact_type = models.CharField(
        _("Contact Type"),
        max_length=20,
        choices=ContactType.choices,
        default=ContactType.SECTION,
        help_text=_("Type of contact: Campus, Department, or Section/Unit")
    )
    
    # Foreign key to Department (optional - for departmental contacts only)
    department = models.ForeignKey(
        'department.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contact_numbers',
        verbose_name=_("Department"),
        help_text=_("Link to Department (only for department type contacts)")
    )
    
    # Name field - required for all types
    name = models.CharField(
        _("Contact Name"), 
        max_length=100,
        help_text=_("Name of the contact (e.g., 'Main Campus', 'Civil Department', 'Library')")
    )
    
    phone_number = models.CharField(
        _("Phone Number"), 
        max_length=20,
        help_text=_("Phone number for this contact")
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

    def save(self, *args, **kwargs):
        # Auto-populate name from linked department if it's a department type
        if self.contact_type == ContactType.DEPARTMENT and self.department:
            self.name = self.department.name
        # Set contact_type to DEPARTMENT if department is linked
        if self.department and self.contact_type != ContactType.DEPARTMENT:
            self.contact_type = ContactType.DEPARTMENT
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_contact_type_display()}: {self.name} - {self.phone_number}"

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = _("Phone Number")
        verbose_name_plural = _("Phone Numbers")
        indexes = [
            models.Index(fields=['contact_type', 'is_active']),
            models.Index(fields=['department', 'is_active']),
        ]