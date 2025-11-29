"""
Utility functions for appointments app
"""

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta

from .models import Appointment, AppointmentHistory, OTPVerification
from .constants import ALLOWED_EMAIL_DOMAIN


def send_appointment_notification(appointment, notification_type='created'):
    """
    Send appointment notification emails
    
    Args:
        appointment: Appointment instance
        notification_type: 'created', 'confirmed', 'rejected', 'cancelled'
    """
    
    context = {
        'appointment': appointment,
        'applicant_name': appointment.applicant_name,
        'appointment_date': appointment.appointment_date,
        'appointment_time': appointment.appointment_time,
        'purpose': appointment.purpose,
        'category': appointment.category,
        'official': appointment.official
    }
    
    if notification_type == 'created':
        subject = f'Appointment Request Submitted - {appointment.category}'
        template = 'appointments/email/appointment_created.html'
    elif notification_type == 'confirmed':
        subject = f'Appointment Confirmed - {appointment.category}'
        template = 'appointments/email/appointment_confirmed.html'
    elif notification_type == 'rejected':
        subject = f'Appointment Request Declined - {appointment.category}'
        template = 'appointments/email/appointment_rejected.html'
    elif notification_type == 'cancelled':
        subject = f'Appointment Cancelled - {appointment.category}'
        template = 'appointments/email/appointment_cancelled.html'
    else:
        return False
    
    try:
        # Render HTML email
        html_message = render_to_string(template, context)
        
        # Plain text fallback
        plain_message = f"""
        Dear {appointment.applicant_name},
        
        Your appointment ({notification_type}) details:
        - Category: {appointment.category}
        - Date: {appointment.appointment_date}
        - Time: {appointment.appointment_time}
        - Purpose: {appointment.purpose}
        
        {f"Notes: {appointment.admin_notes}" if appointment.admin_notes else ""}
        
        Best regards,
        TCIOE Appointment System
        """
        
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[appointment.applicant_email],
            fail_silently=False
        )
        return True
        
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def cleanup_expired_otps():
    """
    Clean up expired OTP records (run as a periodic task)
    """
    expired_threshold = timezone.now() - timedelta(hours=1)
    expired_count = OTPVerification.objects.filter(
        created_at__lt=expired_threshold
    ).delete()[0]
    
    return expired_count


def get_appointment_statistics(user=None, date_range=None):
    """
    Get appointment statistics for dashboard
    
    Args:
        user: Filter by user (for department admins)
        date_range: Tuple of (start_date, end_date)
    """
    
    queryset = Appointment.objects.all()
    
    if user and hasattr(user, 'department'):
        queryset = queryset.filter(department=user.department)
    
    if date_range:
        start_date, end_date = date_range
        queryset = queryset.filter(
            appointment_date__range=[start_date, end_date]
        )
    
    stats = {
        'total_appointments': queryset.count(),
        'pending_appointments': queryset.filter(status=Appointment.STATUS_PENDING).count(),
        'confirmed_appointments': queryset.filter(status=Appointment.STATUS_CONFIRMED).count(),
        'completed_appointments': queryset.filter(status=Appointment.STATUS_COMPLETED).count(),
        'cancelled_appointments': queryset.filter(
            status__in=[Appointment.STATUS_CANCELLED, Appointment.STATUS_REJECTED]
        ).count(),
    }
    
    return stats


def validate_appointment_time_slot(slot, appointment_date, appointment_time):
    """
    Validate if a time slot is available for booking
    
    Args:
        slot: AppointmentSlot instance
        appointment_date: Date object
        appointment_time: Time object
    
    Returns:
        tuple: (is_valid, error_message)
    """
    
    # Check if date matches slot weekday
    if appointment_date.weekday() != slot.weekday:
        return False, "Appointment date must match slot weekday"
    
    # Check if time is within slot hours
    if not (slot.start_time <= appointment_time <= slot.end_time):
        return False, "Appointment time must be within slot hours"
    
    # Check if slot is already booked
    existing_appointment = Appointment.objects.filter(
        slot=slot,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_CONFIRMED]
    ).exists()
    
    if existing_appointment:
        return False, "Time slot is already booked"
    
    return True, ""


def get_available_time_slots(slot, target_date):
    """
    Get all available time slots for a given slot and date
    
    Args:
        slot: AppointmentSlot instance
        target_date: Date object
    
    Returns:
        list: Available time slots as strings (HH:MM format)
    """
    
    if target_date.weekday() != slot.weekday:
        return []
    
    available_times = []
    from datetime import datetime, timedelta
    
    start_datetime = datetime.combine(target_date, slot.start_time)
    end_datetime = datetime.combine(target_date, slot.end_time)
    
    current_time = start_datetime
    while current_time + timedelta(minutes=slot.duration_minutes) <= end_datetime:
        # Check if this time slot is available
        is_valid, _ = validate_appointment_time_slot(
            slot, target_date, current_time.time()
        )
        
        if is_valid:
            available_times.append(current_time.strftime('%H:%M'))
        
        current_time += timedelta(minutes=slot.duration_minutes)
    
    return available_times


def create_appointment_with_history(appointment_data, created_by=None):
    """
    Create an appointment and initial history record
    
    Args:
        appointment_data: Dictionary of appointment data
        created_by: User who created the appointment (optional)
    
    Returns:
        Appointment instance
    """
    
    appointment = Appointment.objects.create(**appointment_data)
    
    # Create initial history record
    AppointmentHistory.objects.create(
        appointment=appointment,
        status=appointment.status,
        notes="Appointment created",
        changed_by=created_by
    )
    
    return appointment


def update_appointment_status(appointment, new_status, admin_notes="", changed_by=None):
    """
    Update appointment status and create history record
    
    Args:
        appointment: Appointment instance
        new_status: New status string
        admin_notes: Optional admin notes
        changed_by: User making the change
    
    Returns:
        Updated appointment instance
    """
    
    old_status = appointment.status
    appointment.status = new_status
    appointment.admin_notes = admin_notes
    
    if new_status == Appointment.STATUS_CONFIRMED and changed_by:
        appointment.confirmed_by = changed_by
        appointment.confirmed_at = timezone.now()
    
    appointment.save()
    
    # Create history record
    AppointmentHistory.objects.create(
        appointment=appointment,
        status=new_status,
        notes=admin_notes or f"Status changed from {old_status} to {new_status}",
        changed_by=changed_by
    )
    
    # Send notification email
    if old_status != new_status:
        notification_type = {
            Appointment.STATUS_CONFIRMED: 'confirmed',
            Appointment.STATUS_REJECTED: 'rejected',
            Appointment.STATUS_CANCELLED: 'cancelled',
        }.get(new_status)
        
        if notification_type:
            send_appointment_notification(appointment, notification_type)
    
    return appointment