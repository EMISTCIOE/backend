from django.urls import path, include
from . import views

# Public URLs (accessible without authentication)
public_urls = [
    # Categories and slots
    path('categories/', views.AppointmentCategoryListView.as_view(), name='appointment-categories'),
    path('slots/', views.AppointmentSlotListView.as_view(), name='appointment-slots'),
    path('departments/', views.departments_list, name='departments-list'),
    path('available-slots/', views.AvailableSlotsView.as_view(), name='available-slots'),
    
    # OTP verification
    path('otp/request/', views.OTPRequestView.as_view(), name='otp-request'),
    path('otp/verify/', views.OTPVerifyView.as_view(), name='otp-verify'),
    
    # Appointment booking
    path('book/', views.AppointmentCreateView.as_view(), name='appointment-create'),
    path('details/<str:verification_token>/', views.AppointmentDetailView.as_view(), name='appointment-detail'),
    
    # Statistics
    path('stats/', views.appointment_stats, name='appointment-stats'),
]

# Admin URLs (require authentication)
admin_urls = [
    path('list/', views.AdminAppointmentListView.as_view(), name='admin-appointment-list'),
    path('<int:pk>/', views.AdminAppointmentDetailView.as_view(), name='admin-appointment-detail'),
    path('<int:appointment_id>/history/', views.AppointmentHistoryView.as_view(), name='appointment-history'),
]

urlpatterns = [
    path('public/', include(public_urls)),
    path('admin/', include(admin_urls)),
]