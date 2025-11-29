"""
Management command to automatically reject appointments that are overdue.
This command should be run daily via cron to automatically reject appointments
that haven't been approved within 2 days after their scheduled date.

Role-based filtering:
- ADMIN: Can see all appointments
- DEPARTMENT_ADMIN: Can see appointments for their department
- Campus officials (based on designation): See appointments for their specific role
- Others: See appointments where they are the assigned official
"""

from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.db.models import Q

from src.appointments.models import Appointment
from src.user.constants import (
    ADMIN_ROLE, 
    DEPARTMENT_ADMIN_ROLE, 
    CAMPUS_UNIT_ROLE, 
    CAMPUS_SECTION_ROLE,
    EMIS_STAFF_ROLE
)


class Command(BaseCommand):
    help = 'Automatically reject appointments not approved within 2 days after scheduled date'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=2,
            help='Number of days after appointment date to auto-reject (default: 2)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be rejected without actually rejecting',
        )

    def handle(self, *args, **options):
        days_threshold = options['days']
        dry_run = options['dry_run']
        
        # Calculate the cutoff date (today - threshold days)
        cutoff_date = date.today() - timedelta(days=days_threshold)
        
        self.stdout.write(f"Looking for pending appointments scheduled before {cutoff_date}...")
        
        # Find pending appointments that are overdue
        overdue_appointments = Appointment.objects.filter(
            status='PENDING',
            appointment_date__lt=cutoff_date
        ).select_related('slot', 'category', 'department')
        
        count = overdue_appointments.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('No overdue appointments found.')
            )
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"DRY RUN: Would reject {count} appointments:")
            )
            for appointment in overdue_appointments:
                self.stdout.write(
                    f"  - ID {appointment.id}: {appointment.applicant_name} "
                    f"on {appointment.appointment_date} at {appointment.appointment_time}"
                )
            return
        
        # Auto-reject overdue appointments
        with transaction.atomic():
            rejected_count = 0
            for appointment in overdue_appointments:
                try:
                    appointment.status = 'REJECTED'
                    appointment.admin_notes = (
                        f"Automatically rejected on {timezone.now().date()} - "
                        f"No approval received within {days_threshold} days after scheduled date."
                    )
                    appointment.updated_at = timezone.now()
                    appointment.save(update_fields=['status', 'admin_notes', 'updated_at'])
                    
                    rejected_count += 1
                    
                    self.stdout.write(
                        f"Rejected appointment ID {appointment.id}: {appointment.applicant_name} "
                        f"scheduled for {appointment.appointment_date}"
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error rejecting appointment ID {appointment.id}: {str(e)}"
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully auto-rejected {rejected_count} out of {count} overdue appointments."
            )
        )
        
        # Show summary statistics
        self.stdout.write("\n" + "="*50)
        self.stdout.write("SUMMARY:")
        self.stdout.write(f"Cutoff date: {cutoff_date}")
        self.stdout.write(f"Appointments processed: {count}")
        self.stdout.write(f"Appointments rejected: {rejected_count}")
        self.stdout.write("="*50)