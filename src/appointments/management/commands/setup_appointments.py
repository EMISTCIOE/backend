from django.core.management.base import BaseCommand
from django.db import transaction

from src.appointments.models import AppointmentCategory, AppointmentSlot
from src.user.models import User
from src.user.constants import ADMIN_ROLE, DEPARTMENT_ADMIN_ROLE
from src.department.models import Department


class Command(BaseCommand):
    help = 'Setup initial appointment categories and slots'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-slots',
            action='store_true',
            help='Create example appointment slots for existing officials',
        )

    def handle(self, *args, **options):
        self.stdout.write("Setting up appointment system...")
        
        with transaction.atomic():
            # Create appointment categories
            self.create_categories()
            
            if options['create_slots']:
                self.create_example_slots()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up appointment system!')
        )

    def create_categories(self):
        """Create appointment categories based on active campus designations"""
        self.stdout.write("Setting up appointment categories from campus designations...")
        
        # Use the sync logic to create categories
        from src.website.models import CampusStaffDesignation
        
        active_designations = CampusStaffDesignation.objects.filter(is_active=True)
        
        if not active_designations.exists():
            self.stdout.write(
                self.style.WARNING(
                    'No active campus designations found. Please create campus designations first.\n'
                    'You can add them via: /admin/website/campusstaffdesignation/'
                )
            )
            return
        
        created_count = 0
        
        for designation in active_designations:
            category, created = AppointmentCategory.objects.get_or_create(
                name=designation.code,
                defaults={
                    'description': f'Appointments with {designation.title}',
                    'linked_designation': designation,
                    'is_active': True,
                    'max_appointments_per_day': 5,
                    'default_duration_minutes': 30,
                    'advance_booking_days': 7,
                    'requires_approval': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"  ✅ Created category: {designation.code} -> {designation.title}")
            else:
                self.stdout.write(f"  ⏭️  Category already exists: {designation.code}")
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"Created {created_count} appointment categories.")
            )
        else:
            self.stdout.write("All appointment categories already exist.")

    def create_example_slots(self):
        """Create example appointment slots based on dynamic categories"""
        self.stdout.write("Creating appointment slots based on active categories...")
        
        # Get all active categories
        categories = AppointmentCategory.objects.filter(is_active=True)
        
        if not categories.exists():
            self.stdout.write(
                self.style.WARNING('No active appointment categories found. Please run sync_appointment_categories first.')
            )
            return
        
        created_slots = 0
        
        for category in categories:
            # Get officials for this category (users with matching designation)
            if category.linked_designation:
                officials = category.linked_designation.users.filter(is_active=True)[:2]  # Max 2 per designation
            else:
                # Fallback for categories without linked designation
                officials = User.objects.filter(role=ADMIN_ROLE)[:1]
            
            if not officials.exists():
                self.stdout.write(f"  ⚠️  No officials found for category: {category.name}")
                continue
            
            # Create slots for each official
            for official in officials:
                slots_created = self.create_slots_for_official(official, category, None, None)
                created_slots += slots_created
                self.stdout.write(f"  ✅ Created {slots_created} slots for {official.get_full_name()} - {category.display_name}")
        
        self.stdout.write(
            self.style.SUCCESS(f"Created {created_slots} appointment slots total.")
        )

    def create_slots_for_official(self, official, category, department, office_identifier=None):
        """Create appointment slots for an official"""
        created_count = 0
        # Create slots for Monday to Friday (0-4)
        weekdays = [0, 1, 2, 3, 4]  # Monday to Friday
        
        for weekday in weekdays:
            # Morning slot: 9:00 AM - 12:00 PM
            morning_slot, created = AppointmentSlot.objects.get_or_create(
                category=category,
                official=official,
                department=department,
                weekday=weekday,
                start_time='09:00',
                end_time='12:00',
                defaults={
                    'duration_minutes': 30,
                    'is_active': True,
                    'office_identifier': office_identifier or '',
                }
            )
            if created:
                created_count += 1
            
            # Afternoon slot: 2:00 PM - 5:00 PM
            afternoon_slot, created = AppointmentSlot.objects.get_or_create(
                category=category,
                official=official,
                department=department,
                weekday=weekday,
                start_time='14:00',
                end_time='17:00',
                defaults={
                    'duration_minutes': 30,
                    'is_active': True,
                    'office_identifier': office_identifier or '',
                }
            )
            if created:
                created_count += 1
        
        return created_count