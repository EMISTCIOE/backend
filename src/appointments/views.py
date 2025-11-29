from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.db import transaction
from datetime import datetime, timedelta
from django.db.models import Q

from .models import (
    AppointmentCategory,
    AppointmentSlot,
    Appointment,
    AppointmentHistory,
    OTPVerification
)
from .serializers import (
    AppointmentCategorySerializer,
    AppointmentSlotSerializer,
    AppointmentCreateSerializer,
    AppointmentSerializer,
    AppointmentAdminSerializer,
    AppointmentStatusUpdateSerializer,
    AppointmentHistorySerializer,
    OTPRequestSerializer,
    OTPVerificationSerializer,
    AvailableSlotsSerializer
)
from .constants import ALLOWED_EMAIL_DOMAIN
from src.user.constants import ADMIN_ROLE, DEPARTMENT_ADMIN_ROLE
from dateutil import parser


class AppointmentConflictCheckView(APIView):
    """Check for appointment conflicts at a specific datetime"""
    
    permission_classes = [permissions.AllowAny]  # Public access
    
    def get(self, request):
        appointment_datetime_str = request.GET.get('appointment_datetime')
        category_id = request.GET.get('category')
        department_id = request.GET.get('department')
        status_filter = request.GET.get('status', 'approved')
        
        if not appointment_datetime_str or not category_id:
            return Response({
                'hasConflict': False,
                'message': 'Missing required parameters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Parse the datetime string
            appointment_datetime = parser.isoparse(appointment_datetime_str)
        except ValueError:
            return Response({
                'hasConflict': False,
                'message': 'Invalid datetime format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Build query for conflicting appointments
        conflict_query = Q(appointment_datetime=appointment_datetime)
        conflict_query &= Q(category_id=category_id)
        
        # Only check approved appointments if status filter is set
        if status_filter == 'approved':
            conflict_query &= Q(status='CONFIRMED')
        
        # Add department filter if provided
        if department_id:
            conflict_query &= Q(department_id=department_id)
        
        # Check for conflicts
        conflicting_appointments = Appointment.objects.filter(conflict_query)
        
        has_conflict = conflicting_appointments.exists()
        
        response_data = {
            'hasConflict': has_conflict,
            'conflictCount': conflicting_appointments.count()
        }
        
        if has_conflict:
            response_data['message'] = 'There is already an approved appointment at this time. Please select a different date and time.'
        
        return Response(response_data)


class AppointmentCategoryListView(generics.ListAPIView):
    """List all active appointment categories ordered by priority"""
    
    serializer_class = AppointmentCategorySerializer
    permission_classes = [permissions.AllowAny]  # Public access
    
    def get_queryset(self):
        return AppointmentCategory.objects.filter(
            is_active=True
        ).select_related('linked_designation').order_by(
            'linked_designation__appointment_priority', 
            'name'
        )


class AppointmentSlotListView(generics.ListAPIView):
    """List appointment slots based on category and date"""
    
    serializer_class = AppointmentSlotSerializer
    permission_classes = [permissions.AllowAny]  # Public access
    
    def get_queryset(self):
        queryset = AppointmentSlot.objects.filter(is_active=True)
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by department (for department head appointments)
        department_id = self.request.query_params.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        # Filter by date to show only slots for that weekday
        date_str = self.request.query_params.get('date')
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                weekday = target_date.weekday()
                queryset = queryset.filter(weekday=weekday)
            except ValueError:
                pass
        
        return queryset.select_related('category', 'official', 'department')


class OTPRequestView(APIView):
    """Request OTP for email verification"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            # Generate OTP
            otp = OTPVerification.generate_otp(email)
            
            # Send OTP email
            try:
                self.send_otp_email(email, otp.otp_code)
                return Response({
                    'message': 'OTP sent successfully',
                    'expires_in_minutes': 10
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'error': 'Failed to send OTP email'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def send_otp_email(self, email, otp_code):
        """Send OTP verification email"""
        from django.template.loader import render_to_string
        
        subject = 'TCIOE EMIS - Appointment Booking OTP'
        
        # Use the HTML template
        html_message = render_to_string('appointments/email/otp_verification.html', {
            'otp_code': otp_code,
        })
        
        # Fallback plain text message
        message = f'''
TCIOE EMIS - Appointment Booking OTP

Your OTP for appointment booking is: {otp_code}

This OTP will expire in 10 minutes.

If you did not request this OTP, please ignore this email.

--
TCIOE EMIS
Tribhuvan University, Central Campus Institute of Engineering
        '''.strip()
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False
        )


class OTPVerifyView(APIView):
    """Verify OTP code"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp_code']
            
            try:
                otp = OTPVerification.objects.get(
                    email=email,
                    otp_code=otp_code,
                    is_active=True
                )
                
                if otp.is_valid():
                    return Response({
                        'message': 'OTP verified successfully',
                        'valid': True
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'error': 'OTP has expired',
                        'valid': False
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except OTPVerification.DoesNotExist:
                return Response({
                    'error': 'Invalid OTP',
                    'valid': False
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppointmentCreateView(generics.CreateAPIView):
    """Create a new appointment"""
    
    serializer_class = AppointmentCreateSerializer
    permission_classes = [permissions.AllowAny]  # Public access
    
    def perform_create(self, serializer):
        """Send confirmation email after creating appointment"""
        appointment = serializer.save()
        
        try:
            self.send_appointment_confirmation_email(appointment)
        except Exception as e:
            # Log the error but don't fail the appointment creation
            print(f"Failed to send confirmation email: {e}")
    
    def send_appointment_confirmation_email(self, appointment):
        """Send appointment confirmation email"""
        subject = f'Appointment Request Submitted - {appointment.category}'
        
        context = {
            'appointment': appointment,
            'applicant_name': appointment.applicant_name,
            'appointment_datetime': appointment.appointment_datetime,
            'purpose': appointment.purpose,
        }
        
        # Send to applicant
        appointment_datetime_str = appointment.appointment_datetime.strftime('%Y-%m-%d %I:%M %p')
        
        applicant_message = f'''
        Dear {appointment.applicant_name},
        
        Your appointment request has been submitted successfully.
        
        Details:
        - Category: {appointment.category}
        - Date & Time: {appointment_datetime_str}
        - Purpose: {appointment.purpose}
        
        Your appointment is currently pending approval. You will receive an email once it's confirmed.
        
        Best regards,
        TCIOE Appointment System
        '''
        
        send_mail(
            subject=subject,
            message=applicant_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[appointment.applicant_email],
            fail_silently=False
        )
        
        # Send to official
        if appointment.official and appointment.official.email:
            official_message = f'''
            Dear {appointment.official.first_name or 'Official'},
            
            A new appointment request has been submitted for you.
            
            Details:
            - Applicant: {appointment.applicant_name} ({appointment.applicant_email})
            - Date: {appointment.appointment_date}
            - Time: {appointment.appointment_time}
            - Purpose: {appointment.purpose}
            - Details: {appointment.details}
            
            Please review and respond to this appointment request in the admin panel.
            
            Best regards,
            TCIOE Appointment System
            '''
            
            send_mail(
                subject=f'New Appointment Request from {appointment.applicant_name}',
                message=official_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[appointment.official.email],
                fail_silently=False
            )


class AppointmentDetailView(generics.RetrieveAPIView):
    """Get appointment details by verification token"""
    
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'verification_token'
    
    def get_queryset(self):
        return Appointment.objects.select_related(
            'category', 'slot', 'slot__official', 'department'
        )


class AvailableSlotsView(APIView):
    """Get available time slots for a specific date and category"""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        serializer = AvailableSlotsSerializer(data=request.query_params)
        if serializer.is_valid():
            date = serializer.validated_data['date']
            category_id = serializer.validated_data['category']
            department_id = serializer.validated_data.get('department')
            
            # Get slots for the weekday
            weekday = date.weekday()
            slots_queryset = AppointmentSlot.objects.filter(
                category_id=category_id,
                weekday=weekday,
                is_active=True
            )
            
            if department_id:
                slots_queryset = slots_queryset.filter(department_id=department_id)
            
            slots = slots_queryset.select_related('category', 'official', 'department')
            
            # Add date context for available times calculation
            serializer = AppointmentSlotSerializer(
                slots, many=True, context={'request': request}
            )
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Admin Views (require authentication)

class AdminAppointmentListView(generics.ListAPIView):
    """List appointments for admin users"""
    
    serializer_class = AppointmentAdminSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.select_related(
            'category', 'slot', 'slot__official', 'department', 'confirmed_by'
        )
        
        # Filter based on user role and position
        if user.has_role(ADMIN_ROLE):
            # System admin can see all appointments
            pass
        elif user.has_role(DEPARTMENT_ADMIN_ROLE):
            # Department admin can see their department's appointments
            queryset = queryset.filter(
                Q(slot__official=user) | Q(department=user.department)
            )
        else:
            # Check if user is an official who can receive appointments
            # Filter to show only appointments for this specific official
            queryset = queryset.filter(slot__official=user)
            
            # Additional filtering based on user's designation
            if hasattr(user, 'designation') and user.designation:
                # Filter appointments to categories linked to user's designation
                queryset = queryset.filter(
                    category__linked_designation=user.designation
                )
            else:
                # If no designation, show only appointments where user is explicitly assigned
                queryset = queryset.filter(slot__official=user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by department (additional filtering for system admins)
        department_filter = self.request.query_params.get('department')
        if department_filter and user.has_role(ADMIN_ROLE):
            queryset = queryset.filter(department_id=department_filter)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(appointment_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(appointment_date__lte=date_to)
        
        return queryset.order_by('-created_at')


class AdminAppointmentDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update appointment details for admin"""
    
    serializer_class = AppointmentStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.select_related(
            'category', 'slot', 'slot__official', 'department'
        )
        
        # Filter based on user role
        if user.has_role(ADMIN_ROLE):
            return queryset
        elif user.has_role(DEPARTMENT_ADMIN_ROLE):
            return queryset.filter(
                Q(slot__official=user) | Q(department=user.department)
            )
        else:
            return queryset.filter(slot__official=user)
    
    def perform_update(self, serializer):
        """Send notification email after status update"""
        old_status = self.get_object().status
        appointment = serializer.save()
        
        # Send email if status changed
        if old_status != appointment.status:
            try:
                self.send_status_update_email(appointment, old_status)
            except Exception as e:
                print(f"Failed to send status update email: {e}")
    
    def send_status_update_email(self, appointment, old_status):
        """Send email notification for status update"""
        status_messages = {
            Appointment.STATUS_CONFIRMED: 'Your appointment has been confirmed!',
            Appointment.STATUS_REJECTED: 'Your appointment request has been declined.',
            Appointment.STATUS_CANCELLED: 'Your appointment has been cancelled.',
            Appointment.STATUS_COMPLETED: 'Your appointment has been completed.',
        }
        
        subject = f'Appointment Status Update - {appointment.category}'
        message = f'''
        Dear {appointment.applicant_name},
        
        {status_messages.get(appointment.status, 'Your appointment status has been updated.')}
        
        Appointment Details:
        - Category: {appointment.category}
        - Date: {appointment.appointment_date}
        - Time: {appointment.appointment_time}
        - Status: {appointment.get_status_display()}
        
        {f"Notes: {appointment.admin_notes}" if appointment.admin_notes else ""}
        
        Best regards,
        TCIOE Appointment System
        '''
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[appointment.applicant_email],
            fail_silently=False
        )


class AppointmentHistoryView(generics.ListAPIView):
    """Get appointment history"""
    
    serializer_class = AppointmentHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        appointment_id = self.kwargs['appointment_id']
        return AppointmentHistory.objects.filter(
            appointment_id=appointment_id
        ).select_related('changed_by').order_by('-created_at')


# Public API views for frontend

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def departments_list(request):
    """Get list of departments for department head appointments"""
    from src.department.models import Department
    departments = Department.objects.filter(is_active=True).values('id', 'name', 'short_name')
    return Response(list(departments))


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def appointment_stats(request):
    """Get basic appointment statistics (for public dashboard)"""
    today = timezone.now().date()
    
    stats = {
        'total_pending': Appointment.objects.filter(
            status=Appointment.STATUS_PENDING
        ).count(),
        'today_appointments': Appointment.objects.filter(
            appointment_date=today,
            status__in=[Appointment.STATUS_CONFIRMED, Appointment.STATUS_COMPLETED]
        ).count(),
        'categories': []
    }
    
    # Get category-wise stats
    for category in AppointmentCategory.objects.filter(is_active=True):
        category_stats = {
            'name': category.get_name_display(),
            'pending_count': Appointment.objects.filter(
                category=category,
                status=Appointment.STATUS_PENDING
            ).count(),
            'available_slots_today': AppointmentSlot.objects.filter(
                category=category,
                weekday=today.weekday(),
                is_active=True
            ).count()
        }
        stats['categories'].append(category_stats)
    
    return Response(stats)