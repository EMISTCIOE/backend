from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from src.appointments.models import Appointment


class Command(BaseCommand):
    help = 'Test email sending functionality'

    def handle(self, *args, **options):
        self.stdout.write('Testing email functionality...')
        
        try:
            # Create a simple test email
            email = EmailMultiAlternatives(
                subject='Test Email from TCIOE EMIS',
                body='This is a test email to verify SMTP configuration.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=['test@tcioe.edu.np']  # Replace with a real email for testing
            )
            email.send(fail_silently=False)
            self.stdout.write(self.style.SUCCESS('✅ Test email sent successfully!'))
            
            # Test appointment template rendering
            try:
                # Get a sample appointment or create dummy data
                appointments = Appointment.objects.all()
                if appointments.exists():
                    appointment = appointments.first()
                    context = {
                        'appointment': appointment,
                        'applicant_name': appointment.applicant_name,
                        'appointment_datetime': appointment.appointment_datetime,
                        'purpose': appointment.purpose,
                        'current_year': timezone.now().year,
                    }
                    
                    # Test template rendering
                    html_content = render_to_string('appointments/email/appointment_created.html', context)
                    self.stdout.write(self.style.SUCCESS('✅ Template rendering works!'))
                    
                    # Test notification template
                    notification_html = render_to_string('appointments/email/appointment_notification.html', context)
                    self.stdout.write(self.style.SUCCESS('✅ Notification template rendering works!'))
                    
                else:
                    self.stdout.write(self.style.WARNING('⚠️ No appointments found to test templates'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Template error: {e}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Email sending failed: {e}'))