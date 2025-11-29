from rest_framework import serializers
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

from .models import (
    AppointmentCategory,
    AppointmentSlot,
    Appointment,
    AppointmentHistory,
    OTPVerification
)
from .constants import ALLOWED_EMAIL_DOMAIN
from src.user.models import User
from src.department.models import Department


class AppointmentCategorySerializer(serializers.ModelSerializer):
    """Serializer for appointment categories"""
    
    display_name = serializers.ReadOnlyField()
    priority = serializers.IntegerField(source='linked_designation.appointment_priority', read_only=True)
    
    class Meta:
        model = AppointmentCategory
        fields = [
            'id', 'name', 'description', 'display_name', 'is_active', 
            'max_appointments_per_day', 'priority', 'requires_approval',
            'default_duration_minutes', 'advance_booking_days'
        ]


class DepartmentMinimalSerializer(serializers.ModelSerializer):
    """Minimal department serializer for appointment slots"""
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'short_name']


class OfficialMinimalSerializer(serializers.ModelSerializer):
    """Minimal official serializer with identifying information but preserving privacy"""
    
    designation_name = serializers.CharField(
        source='designation.title', read_only=True
    )
    area_of_responsibility = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'designation_name', 'area_of_responsibility']
    
    def get_area_of_responsibility(self, obj):
        """Get the area of responsibility for Assistant Campus Chiefs"""
        if obj.designation and "Assistant Campus Chief" in obj.designation.title:
            # Map based on the person's name/role
            if "Administration" in obj.designation.title:
                return "Administration"
            elif "Academic" in obj.designation.title:
                return "Academic"
            elif "Planning" in obj.designation.title or "Resource" in obj.designation.title:
                return "Planning & Resource"
            else:
                # Fallback: try to determine from appointment slots
                from .models import AppointmentCategory
                slot = obj.appointment_slots.first()
                if slot:
                    if slot.category.name == AppointmentCategory.ASSISTANT_CAMPUS_CHIEF_ADMIN:
                        return "Administration"
                    elif slot.category.name == AppointmentCategory.ASSISTANT_CAMPUS_CHIEF_ACADEMIC:
                        return "Academic"
                    elif slot.category.name == AppointmentCategory.ASSISTANT_CAMPUS_CHIEF_PLANNING:
                        return "Planning & Resource"
                return "General"
        return None


class AppointmentSlotSerializer(serializers.ModelSerializer):
    """Serializer for appointment slots"""
    
    category = AppointmentCategorySerializer(read_only=True)
    department = DepartmentMinimalSerializer(read_only=True) 
    official = OfficialMinimalSerializer(read_only=True)
    weekday_display = serializers.CharField(source='get_weekday_display', read_only=True)
    available_times = serializers.SerializerMethodField()
    slot_display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AppointmentSlot
        fields = [
            'id', 'category', 'department', 'official', 'weekday',
            'weekday_display', 'start_time', 'end_time', 'duration_minutes',
            'available_times', 'office_identifier', 'slot_display_name'
        ]
    
    def get_slot_display_name(self, obj):
        """Generate a clear display name for the slot"""
        base_name = f"{obj.start_time} - {obj.end_time}"
        
        if obj.official and obj.official.designation:
            designation = obj.official.designation.title
            
            # For Campus Chief, simple display
            if "Campus Chief" in designation and "Assistant" not in designation:
                return f"{base_name} ({designation})"
            
            # For Assistant Campus Chiefs, add distinguishing info
            elif "Assistant" in designation:
                if obj.office_identifier:
                    return f"{base_name} ({designation} - {obj.office_identifier})"
                else:
                    # Use the helper method to get assistant number
                    assistant_number = self._get_assistant_number(obj.official)
                    return f"{base_name} ({designation} #{assistant_number})"
            
            # For Department Heads, show with department
            elif obj.department:
                return f"{base_name} ({designation} - {obj.department.name})"
            
            return f"{base_name} ({designation})"
        
        return base_name
    
    def _get_assistant_number(self, user):
        """Get a consistent number for assistant campus chiefs"""
        from src.user.constants import ADMIN_ROLE
        assistants = User.objects.filter(
            role=ADMIN_ROLE,
            designation__title__icontains="Assistant"
        ).order_by('id')
        
        for idx, assistant in enumerate(assistants, 1):
            if assistant.id == user.id:
                return idx
        return 1
    
    def get_available_times(self, obj):
        """Get available time slots for a given date"""
        request = self.context.get('request')
        date_str = request.query_params.get('date') if request else None
        
        if not date_str:
            return []
        
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return []
        
        # Check if the weekday matches
        if target_date.weekday() != obj.weekday:
            return []
        
        # Generate time slots
        available_times = []
        start_datetime = datetime.combine(target_date, obj.start_time)
        end_datetime = datetime.combine(target_date, obj.end_time)
        
        current_time = start_datetime
        while current_time + timedelta(minutes=obj.duration_minutes) <= end_datetime:
            # Check if this time slot is already booked
            is_booked = Appointment.objects.filter(
                slot=obj,
                appointment_date=target_date,
                appointment_time=current_time.time(),
                status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_CONFIRMED]
            ).exists()
            
            if not is_booked:
                available_times.append(current_time.strftime('%H:%M'))
            
            current_time += timedelta(minutes=obj.duration_minutes)
        
        return available_times


class OTPVerificationSerializer(serializers.ModelSerializer):
    """Serializer for OTP verification"""
    
    class Meta:
        model = OTPVerification
        fields = ['email', 'otp_code']
    
    def validate_email(self, value):
        """Validate email domain"""
        if not value.endswith(ALLOWED_EMAIL_DOMAIN):
            raise serializers.ValidationError(
                f"Email must be from {ALLOWED_EMAIL_DOMAIN} domain"
            )
        return value


class OTPRequestSerializer(serializers.Serializer):
    """Serializer for OTP request"""
    
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validate email domain"""
        if not value.endswith(ALLOWED_EMAIL_DOMAIN):
            raise serializers.ValidationError(
                f"Email must be from {ALLOWED_EMAIL_DOMAIN} domain"
            )
        return value


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating appointments"""
    
    otp_code = serializers.CharField(write_only=True, max_length=6)
    
    class Meta:
        model = Appointment
        fields = [
            'applicant_name', 'applicant_email', 'applicant_phone',
            'applicant_designation', 'category', 'slot', 'department',
            'appointment_date', 'appointment_time', 'purpose', 'details',
            'otp_code'
        ]
    
    def validate_applicant_email(self, value):
        """Validate email domain"""
        if not value.endswith(ALLOWED_EMAIL_DOMAIN):
            raise serializers.ValidationError(
                f"Email must be from {ALLOWED_EMAIL_DOMAIN} domain"
            )
        return value
    
    def validate_appointment_date(self, value):
        """Validate appointment date"""
        if value < timezone.now().date():
            raise serializers.ValidationError("Appointment date cannot be in the past")
        
        # Check if date is too far in advance (e.g., max 30 days)
        max_advance_date = timezone.now().date() + timedelta(days=30)
        if value > max_advance_date:
            raise serializers.ValidationError(
                "Appointment date cannot be more than 30 days in advance"
            )
        
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        slot = attrs.get('slot')
        appointment_date = attrs.get('appointment_date')
        appointment_time = attrs.get('appointment_time')
        category = attrs.get('category')
        department = attrs.get('department')
        otp_code = attrs.get('otp_code')
        applicant_email = attrs.get('applicant_email')
        
        # Validate OTP
        if otp_code and applicant_email:
            try:
                otp = OTPVerification.objects.get(
                    email=applicant_email,
                    otp_code=otp_code,
                    is_active=True
                )
                if not otp.is_valid():
                    raise serializers.ValidationError(
                        {"otp_code": "OTP has expired or is invalid"}
                    )
            except OTPVerification.DoesNotExist:
                raise serializers.ValidationError(
                    {"otp_code": "Invalid OTP code"}
                )
        
        # Validate slot category matches appointment category
        if slot and category and slot.category != category:
            raise serializers.ValidationError(
                {"slot": "Slot category must match appointment category"}
            )
        
        # Validate department requirement for department head appointments
        if (category and category.name == AppointmentCategory.DEPARTMENT_HEAD and 
            not department):
            raise serializers.ValidationError(
                {"department": "Department is required for department head appointments"}
            )
        
        # Validate appointment date/time matches slot weekday
        if slot and appointment_date:
            if appointment_date.weekday() != slot.weekday:
                raise serializers.ValidationError(
                    {"appointment_date": "Appointment date must match slot weekday"}
                )
        
        # Check if time slot is available
        if slot and appointment_date and appointment_time:
            existing_appointment = Appointment.objects.filter(
                slot=slot,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_CONFIRMED]
            ).exists()
            
            if existing_appointment:
                raise serializers.ValidationError(
                    {"appointment_time": "This time slot is already booked"}
                )
        
        # Validate appointment time is within slot hours
        if slot and appointment_time:
            if not (slot.start_time <= appointment_time <= slot.end_time):
                raise serializers.ValidationError(
                    {"appointment_time": "Appointment time must be within slot hours"}
                )
        
        return attrs
    
    def create(self, validated_data):
        """Create appointment and mark OTP as verified"""
        otp_code = validated_data.pop('otp_code')
        applicant_email = validated_data['applicant_email']
        
        # Mark OTP as verified
        otp = OTPVerification.objects.get(
            email=applicant_email,
            otp_code=otp_code,
            is_active=True
        )
        otp.is_verified = True
        otp.save()
        
        # Create appointment with email verified
        appointment = Appointment.objects.create(
            email_verified=True,
            **validated_data
        )
        
        # Create history record
        AppointmentHistory.objects.create(
            appointment=appointment,
            status=appointment.status,
            notes="Appointment created"
        )
        
        return appointment


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for appointment details"""
    
    category = AppointmentCategorySerializer(read_only=True)
    slot = AppointmentSlotSerializer(read_only=True)
    department = DepartmentMinimalSerializer(read_only=True)
    official = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'applicant_name', 'applicant_email', 'applicant_phone',
            'applicant_designation', 'category', 'slot', 'department',
            'appointment_date', 'appointment_time', 'purpose', 'details',
            'status', 'status_display', 'admin_notes', 'email_verified',
            'official', 'created_at'
        ]
    
    def get_official(self, obj):
        """Get official information"""
        if obj.slot and obj.slot.official:
            return OfficialMinimalSerializer(obj.slot.official).data
        return None


class AppointmentAdminSerializer(AppointmentSerializer):
    """Extended serializer for admin use"""
    
    confirmed_by = serializers.StringRelatedField(read_only=True)
    confirmed_at = serializers.DateTimeField(read_only=True)
    
    class Meta(AppointmentSerializer.Meta):
        fields = AppointmentSerializer.Meta.fields + [
            'confirmed_by', 'confirmed_at', 'verification_token'
        ]


class AppointmentStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating appointment status"""
    
    class Meta:
        model = Appointment
        fields = ['status', 'admin_notes']
    
    def validate_status(self, value):
        """Validate status transition"""
        appointment = self.instance
        if not appointment:
            return value
        
        current_status = appointment.status
        
        # Define valid transitions
        valid_transitions = {
            Appointment.STATUS_PENDING: [
                Appointment.STATUS_CONFIRMED,
                Appointment.STATUS_REJECTED,
                Appointment.STATUS_CANCELLED
            ],
            Appointment.STATUS_CONFIRMED: [
                Appointment.STATUS_COMPLETED,
                Appointment.STATUS_CANCELLED
            ],
            # Other statuses are generally final
        }
        
        if (current_status in valid_transitions and 
            value not in valid_transitions[current_status]):
            raise serializers.ValidationError(
                f"Cannot change status from {current_status} to {value}"
            )
        
        return value
    
    def update(self, instance, validated_data):
        """Update appointment status and create history"""
        old_status = instance.status
        new_status = validated_data.get('status', old_status)
        
        # Update the appointment
        appointment = super().update(instance, validated_data)
        
        # Create history record if status changed
        if old_status != new_status:
            user = self.context.get('request').user if self.context.get('request') else None
            AppointmentHistory.objects.create(
                appointment=appointment,
                status=new_status,
                notes=validated_data.get('admin_notes', ''),
                changed_by=user
            )
            
            # Set confirmed_by and confirmed_at for confirmed status
            if new_status == Appointment.STATUS_CONFIRMED and user:
                appointment.confirmed_by = user
                appointment.confirmed_at = timezone.now()
                appointment.save()
        
        return appointment


class AppointmentHistorySerializer(serializers.ModelSerializer):
    """Serializer for appointment history"""
    
    changed_by = serializers.StringRelatedField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AppointmentHistory
        fields = [
            'id', 'status', 'status_display', 'notes', 'changed_by', 'created_at'
        ]
        read_only_fields = fields


class AvailableSlotsSerializer(serializers.Serializer):
    """Serializer for checking available slots"""
    
    date = serializers.DateField()
    category = serializers.IntegerField()
    department = serializers.IntegerField(required=False)
    
    def validate_date(self, value):
        """Validate date is not in past"""
        if value < timezone.now().date():
            raise serializers.ValidationError("Date cannot be in the past")
        return value