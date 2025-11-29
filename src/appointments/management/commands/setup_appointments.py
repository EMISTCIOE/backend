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
        """Create appointment categories"""
        categories_data = [
            {
                'name': AppointmentCategory.CAMPUS_CHIEF,
                'description': 'Appointments with the Campus Chief for administrative matters',
                'max_appointments_per_day': 5,
            },
            {
                'name': AppointmentCategory.ASSISTANT_CAMPUS_CHIEF_ADMIN,
                'description': 'Appointments with Assistant Campus Chief for Administration matters',
                'max_appointments_per_day': 8,
            },
            {
                'name': AppointmentCategory.ASSISTANT_CAMPUS_CHIEF_ACADEMIC,
                'description': 'Appointments with Assistant Campus Chief for Academic matters',
                'max_appointments_per_day': 8,
            },
            {
                'name': AppointmentCategory.ASSISTANT_CAMPUS_CHIEF_PLANNING,
                'description': 'Appointments with Assistant Campus Chief for Planning & Resource matters',
                'max_appointments_per_day': 8,
            },
            {
                'name': AppointmentCategory.DEPARTMENT_HEAD,
                'description': 'Appointments with Department Heads for academic and departmental matters',
                'max_appointments_per_day': 10,
            },
        ]
        
        for category_data in categories_data:
            category, created = AppointmentCategory.objects.get_or_create(
                name=category_data['name'],
                defaults=category_data
            )
            
            if created:
                self.stdout.write(
                    f"Created category: {category.get_name_display()}"
                )
            else:
                self.stdout.write(
                    f"Category already exists: {category.get_name_display()}"
                )

    def create_example_slots(self):
        """Create example appointment slots"""
        self.stdout.write("Creating example appointment slots...")
        
        # Get categories
        campus_chief_cat = AppointmentCategory.objects.get(name=AppointmentCategory.CAMPUS_CHIEF)
        asst_admin_cat = AppointmentCategory.objects.get(name=AppointmentCategory.ASSISTANT_CAMPUS_CHIEF_ADMIN)
        asst_academic_cat = AppointmentCategory.objects.get(name=AppointmentCategory.ASSISTANT_CAMPUS_CHIEF_ACADEMIC)
        asst_planning_cat = AppointmentCategory.objects.get(name=AppointmentCategory.ASSISTANT_CAMPUS_CHIEF_PLANNING)
        dept_head_cat = AppointmentCategory.objects.get(name=AppointmentCategory.DEPARTMENT_HEAD)
        
        # Find users with appropriate roles
        campus_chiefs = User.objects.filter(role=ADMIN_ROLE)[:1]  # 1 campus chief
        assistant_chiefs = User.objects.filter(role=ADMIN_ROLE)[1:4]  # 3 assistant chiefs
        department_heads = User.objects.filter(role=DEPARTMENT_ADMIN_ROLE)[:6]  # 6 dept heads
        
        # Create slots for Campus Chief
        for chief in campus_chiefs:
            self.create_slots_for_official(chief, campus_chief_cat, None, None)
        
        # Create slots for Assistant Campus Chiefs
        assistant_categories = [
            (asst_admin_cat, "Administration"),
            (asst_academic_cat, "Academic"),
            (asst_planning_cat, "Planning & Resource")
        ]
        
        for i, asst_chief in enumerate(assistant_chiefs):
            if i < len(assistant_categories):
                category, area = assistant_categories[i]
                self.create_slots_for_official(asst_chief, category, None, area)
        
        # Create slots for Department Heads
        departments = Department.objects.filter(is_active=True)[:6]
        for i, dept_head in enumerate(department_heads):
            department = departments[i] if i < len(departments) else None
            self.create_slots_for_official(dept_head, dept_head_cat, department, None)

    def create_slots_for_official(self, official, category, department, office_identifier=None):
        """Create appointment slots for an official"""
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
        
        designation = official.designation.title if official.designation else "Official"
        dept_name = f" ({department.name})" if department else ""
        office_info = f" - {office_identifier}" if office_identifier else ""
        
        self.stdout.write(
            f"Created slots for {designation}{office_info}{dept_name} - {category.get_name_display()}"
        )