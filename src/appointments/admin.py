from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import (
    AppointmentCategory,
    AppointmentSlot, 
    Appointment,
    AppointmentHistory,
    OTPVerification
)


@admin.register(AppointmentCategory)
class AppointmentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'max_appointments_per_day', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = [
        'category', 'official', 'office_identifier', 'department', 'get_weekday_display', 
        'start_time', 'end_time', 'duration_minutes', 'is_active'
    ]
    list_filter = ['category', 'weekday', 'is_active', 'official__department']
    search_fields = ['official__email', 'official__first_name', 'official__last_name', 'office_identifier']
    ordering = ['category', 'weekday', 'start_time']
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'official', 'office_identifier', 'department')
        }),
        ('Schedule', {
            'fields': ('weekday', 'start_time', 'end_time', 'duration_minutes')
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'category', 'official', 'department'
        )


class AppointmentHistoryInline(admin.TabularInline):
    model = AppointmentHistory
    extra = 0
    readonly_fields = ['status', 'notes', 'changed_by', 'created_at']
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'applicant_name', 'applicant_email', 'category', 'appointment_date',
        'appointment_time', 'status', 'email_verified', 'created_at'
    ]
    list_filter = [
        'status', 'category', 'email_verified', 'appointment_date',
        'created_at', 'slot__department'
    ]
    search_fields = [
        'applicant_name', 'applicant_email', 'purpose', 
        'slot__official__email', 'slot__official__first_name', 'slot__official__last_name'
    ]
    readonly_fields = [
        'verification_token', 'created_at', 'updated_at', 'confirmed_at'
    ]
    fieldsets = (
        (_('Applicant Information'), {
            'fields': ('applicant_name', 'applicant_email', 'applicant_phone', 'applicant_designation')
        }),
        (_('Appointment Details'), {
            'fields': ('category', 'slot', 'department', 'appointment_date', 'appointment_time')
        }),
        (_('Purpose & Details'), {
            'fields': ('purpose', 'details')
        }),
        (_('Status & Management'), {
            'fields': ('status', 'admin_notes', 'confirmed_by', 'confirmed_at')
        }),
        (_('Verification'), {
            'fields': ('email_verified', 'verification_token')
        }),
        (_('System Information'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    inlines = [AppointmentHistoryInline]
    actions = ['confirm_appointments', 'reject_appointments']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'category', 'slot', 'slot__official', 'department', 'confirmed_by'
        )
    
    def confirm_appointments(self, request, queryset):
        """Bulk confirm appointments"""
        updated = queryset.filter(
            status=Appointment.STATUS_PENDING,
            email_verified=True
        ).update(
            status=Appointment.STATUS_CONFIRMED,
            confirmed_by=request.user,
            confirmed_at=timezone.now()
        )
        
        # Create history records for confirmed appointments
        for appointment in queryset.filter(status=Appointment.STATUS_CONFIRMED):
            AppointmentHistory.objects.create(
                appointment=appointment,
                status=Appointment.STATUS_CONFIRMED,
                notes=f"Bulk confirmed by {request.user}",
                changed_by=request.user
            )
        
        self.message_user(request, f"Confirmed {updated} appointments.")
    
    confirm_appointments.short_description = _("Confirm selected appointments")
    
    def reject_appointments(self, request, queryset):
        """Bulk reject appointments"""
        updated = queryset.filter(
            status=Appointment.STATUS_PENDING
        ).update(status=Appointment.STATUS_REJECTED)
        
        # Create history records for rejected appointments  
        for appointment in queryset.filter(status=Appointment.STATUS_REJECTED):
            AppointmentHistory.objects.create(
                appointment=appointment,
                status=Appointment.STATUS_REJECTED,
                notes=f"Bulk rejected by {request.user}",
                changed_by=request.user
            )
        
        self.message_user(request, f"Rejected {updated} appointments.")
    
    reject_appointments.short_description = _("Reject selected appointments")


@admin.register(AppointmentHistory)
class AppointmentHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'appointment', 'status', 'changed_by', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = [
        'appointment__applicant_name', 'appointment__applicant_email', 'notes'
    ]
    readonly_fields = ['appointment', 'status', 'notes', 'changed_by', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'appointment', 'changed_by'
        )
    
    def has_add_permission(self, request):
        return False


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = [
        'email', 'otp_code', 'is_verified', 'expires_at', 'created_at'
    ]
    list_filter = ['is_verified', 'created_at', 'expires_at']
    search_fields = ['email']
    readonly_fields = ['otp_code', 'expires_at', 'created_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        return False