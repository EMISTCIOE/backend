import random
import string
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from src.base.models import AuditInfoModel
from src.user.models import User
from src.department.models import Department
from src.website.models import CampusStaffDesignation


class AppointmentCategory(models.Model):
    """Categories for different types of appointments - dynamically linked to campus designations"""
    
    name = models.CharField(
        _('Category Name'),
        max_length=150,  # Increased to match CampusStaffDesignation code field
        unique=True,
        help_text=_('Category name that maps to campus designation codes')
    )
    description = models.TextField(
        _('Description'),
        blank=True,
        help_text=_('Description of this appointment category')
    )
    linked_designation = models.ForeignKey(
        CampusStaffDesignation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointment_categories',
        verbose_name=_('Linked Designation'),
        help_text=_('Campus designation this category is linked to (optional)')
    )
    is_active = models.BooleanField(
        _('Is Active'),
        default=True,
        help_text=_('Whether this category is available for booking')
    )
    max_appointments_per_day = models.PositiveIntegerField(
        _('Max Appointments per Day'),
        default=5,
        help_text=_('Maximum appointments allowed per day for this category')
    )
    default_duration_minutes = models.PositiveIntegerField(
        _('Default Duration (minutes)'),
        default=30,
        help_text=_('Default duration for appointments in this category')
    )
    advance_booking_days = models.PositiveIntegerField(
        _('Advance Booking Days'),
        default=7,
        help_text=_('How many days in advance appointments can be booked')
    )
    requires_approval = models.BooleanField(
        _('Requires Approval'),
        default=True,
        help_text=_('Whether appointments in this category require admin approval')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Appointment Category')
        verbose_name_plural = _('Appointment Categories')
        ordering = ['name']
    
    def __str__(self):
        if self.linked_designation:
            return f"{self.linked_designation.title} - {self.description}"
        return f"{self.name} - {self.description}"
    
    @property
    def display_name(self):
        """Human-friendly display name"""
        if self.linked_designation:
            return self.linked_designation.title
        return self.description or self.name
    
    def get_officials(self):
        """Get users who can handle appointments for this category"""
        if self.linked_designation:
            return self.linked_designation.users.filter(is_active=True)
        return User.objects.none()


class AppointmentSlot(models.Model):
    """Time slots available for appointments"""
    
    WEEKDAY_CHOICES = [
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday')),
    ]
    
    category = models.ForeignKey(
        AppointmentCategory,
        on_delete=models.CASCADE,
        related_name='slots',
        verbose_name=_('Category')
    )
    official = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appointment_slots',
        verbose_name=_('Official'),
        help_text=_('The official who will handle this appointment')
    )
    office_identifier = models.CharField(
        _('Office Identifier'),
        max_length=50,
        blank=True,
        help_text=_('Optional identifier to distinguish between officials with same designation (e.g., "Office A", "Block 1", etc.)')
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='appointment_slots',
        verbose_name=_('Department'),
        help_text=_('Required for department head appointments')
    )
    weekday = models.IntegerField(
        _('Weekday'),
        choices=WEEKDAY_CHOICES,
        help_text=_('Day of the week (0=Monday, 6=Sunday)')
    )
    start_time = models.TimeField(_('Start Time'))
    end_time = models.TimeField(_('End Time'))
    duration_minutes = models.PositiveIntegerField(
        _('Duration (Minutes)'),
        default=30,
        help_text=_('Duration of each appointment in minutes')
    )
    is_active = models.BooleanField(
        _('Is Active'),
        default=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Appointment Slot')
        verbose_name_plural = _('Appointment Slots')
        ordering = ['weekday', 'start_time']
        constraints = [
            models.CheckConstraint(
                check=models.Q(start_time__lt=models.F('end_time')),
                name='start_time_before_end_time'
            ),
        ]
    
    def __str__(self):
        official_info = str(self.official)
        if self.office_identifier:
            official_info += f" ({self.office_identifier})"
        return f"{self.get_weekday_display()} {self.start_time}-{self.end_time} - {official_info}"
    
    def clean(self):
        super().clean()
        if self.start_time >= self.end_time:
            raise ValidationError(_('Start time must be before end time'))
        
        if self.category.name == AppointmentCategory.DEPARTMENT_HEAD and not self.department:
            raise ValidationError(_('Department is required for department head appointments'))


class OTPVerification(models.Model):
    """OTP verification for appointment booking"""
    
    email = models.EmailField(_('Email'))
    otp_code = models.CharField(_('OTP Code'), max_length=6)
    is_verified = models.BooleanField(_('Is Verified'), default=False)
    is_active = models.BooleanField(_('Is Active'), default=True)
    expires_at = models.DateTimeField(_('Expires At'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('OTP Verification')
        verbose_name_plural = _('OTP Verifications')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email} - {self.otp_code}"
    
    @classmethod
    def generate_otp(cls, email):
        """Generate a new OTP for the given email"""
        # Deactivate previous OTPs
        cls.objects.filter(email=email, is_verified=False).update(is_active=False)
        
        # Generate 6-digit OTP
        otp_code = ''.join(random.choices(string.digits, k=6))
        expires_at = timezone.now() + timedelta(minutes=10)  # OTP valid for 10 minutes
        
        otp = cls.objects.create(
            email=email,
            otp_code=otp_code,
            expires_at=expires_at
        )
        return otp
    
    def is_valid(self):
        """Check if OTP is still valid"""
        return (
            self.is_active and 
            not self.is_verified and 
            timezone.now() < self.expires_at
        )


class Appointment(models.Model):
    """Appointment booking model"""
    
    STATUS_PENDING = 'PENDING'
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_REJECTED = 'REJECTED'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, _('Pending')),
        (STATUS_CONFIRMED, _('Confirmed')),
        (STATUS_CANCELLED, _('Cancelled')),
        (STATUS_COMPLETED, _('Completed')),
        (STATUS_REJECTED, _('Rejected')),
    ]
    
    # Applicant information
    applicant_name = models.CharField(
        _('Applicant Name'),
        max_length=100
    )
    applicant_email = models.EmailField(
        _('Applicant Email'),
        help_text=_('Must be a @tcioe.edu.np email')
    )
    applicant_phone = models.CharField(
        _('Applicant Phone'),
        max_length=15,
        blank=True
    )
    applicant_designation = models.CharField(
        _('Applicant Designation'),
        max_length=100,
        help_text=_('Position/Role of the applicant')
    )
    
    # Appointment details
    category = models.ForeignKey(
        AppointmentCategory,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('Category')
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='appointments',
        verbose_name=_('Department'),
        help_text=_('Required for department head appointments')
    )
    
    # Appointment timing
    appointment_date = models.DateField(_('Appointment Date'))
    appointment_time = models.CharField(
        _('Preferred Time'),
        max_length=100,
        help_text=_('Preferred appointment time (e.g., "2:00 PM", "14:30", "Morning")')
    )
    # New datetime field - will replace the above fields
    appointment_datetime = models.DateTimeField(
        _('Appointment Date & Time'),
        null=True,
        blank=True,
        help_text=_('Requested appointment date and time')
    )
    
    # Purpose and details
    purpose = models.CharField(
        _('Purpose'),
        max_length=200,
        help_text=_('Brief purpose of the appointment')
    )
    details = models.TextField(
        _('Details'),
        help_text=_('Detailed description of what you want to discuss')
    )
    
    # Status and management
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    admin_notes = models.TextField(
        _('Admin Notes'),
        blank=True,
        help_text=_('Notes from the admin/official')
    )
    confirmed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_appointments',
        verbose_name=_('Confirmed By')
    )
    confirmed_at = models.DateTimeField(
        _('Confirmed At'),
        null=True,
        blank=True
    )
    
    # Verification
    email_verified = models.BooleanField(
        _('Email Verified'),
        default=False
    )
    verification_token = models.CharField(
        _('Verification Token'),
        max_length=100,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Appointment')
        verbose_name_plural = _('Appointments')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['category', 'appointment_date', 'appointment_time'],
                condition=models.Q(status__in=['PENDING', 'CONFIRMED']),
                name='unique_category_datetime_active'
            ),
        ]
    
    def __str__(self):
        return f"{self.applicant_name} - {self.category} - {self.appointment_date}"
    
    def clean(self):
        super().clean()
        
        # Validate email domain
        if not self.applicant_email.endswith('@tcioe.edu.np'):
            raise ValidationError(_('Email must be from @tcioe.edu.np domain'))
        
        # Validate appointment date (not in past)
        if self.appointment_date and self.appointment_date < timezone.now().date():
            raise ValidationError(_('Appointment date cannot be in the past'))
        
        # Validate department for department head appointments
        if (self.category.name == AppointmentCategory.DEPARTMENT_HEAD and 
            not self.department):
            raise ValidationError(_('Department is required for department head appointments'))
        
        # Validate slot and category match
        if self.slot and self.category and self.slot.category != self.category:
            raise ValidationError(_('Slot category must match appointment category'))
    
    def save(self, *args, **kwargs):
        if not self.verification_token:
            self.verification_token = ''.join(random.choices(
                string.ascii_letters + string.digits, k=32
            ))
        super().save(*args, **kwargs)
    
    @property
    def official(self):
        """Get the official for this appointment"""
        return self.slot.official if self.slot else None
    
    def can_be_cancelled(self):
        """Check if appointment can be cancelled"""
        return self.status in [self.STATUS_PENDING, self.STATUS_CONFIRMED]
    
    def can_be_confirmed(self):
        """Check if appointment can be confirmed"""
        return self.status == self.STATUS_PENDING and self.email_verified


class AppointmentHistory(models.Model):
    """Track appointment status changes"""
    
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name=_('Appointment')
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=Appointment.STATUS_CHOICES
    )
    notes = models.TextField(
        _('Notes'),
        blank=True
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointment_changes',
        verbose_name=_('Changed By')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Appointment History')
        verbose_name_plural = _('Appointment Histories')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.appointment} - {self.status}"