"""Constants for appointments app"""

# Email domain for verification
ALLOWED_EMAIL_DOMAIN = "@tcioe.edu.np"

# OTP settings
OTP_LENGTH = 6
OTP_VALIDITY_MINUTES = 10

# Appointment settings
DEFAULT_APPOINTMENT_DURATION = 30  # minutes
MAX_ADVANCE_BOOKING_DAYS = 30  # maximum days in advance to book
MIN_ADVANCE_BOOKING_HOURS = 24  # minimum hours in advance to book

# Appointment limits
MAX_APPOINTMENTS_PER_DAY = 5
MAX_APPOINTMENTS_PER_USER_PER_MONTH = 3

# Email templates
APPOINTMENT_REQUEST_TEMPLATE = "appointments/email/appointment_request.html"
APPOINTMENT_CONFIRMATION_TEMPLATE = "appointments/email/appointment_confirmation.html"
APPOINTMENT_CANCELLATION_TEMPLATE = "appointments/email/appointment_cancellation.html"
OTP_VERIFICATION_TEMPLATE = "appointments/email/otp_verification.html"