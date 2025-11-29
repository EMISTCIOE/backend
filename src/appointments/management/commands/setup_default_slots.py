from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from datetime import time

from src.appointments.models import AppointmentCategory, AppointmentSlot
from src.user.constants import ADMIN_ROLE, DEPARTMENT_ADMIN_ROLE

User = get_user_model()


class Command(BaseCommand):
    help = 'Setup default appointment slots from Sunday to Friday, 10 AM to 4 PM'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up default appointment slots...'))

        # Time slots: 10 AM to 4 PM with 30-minute intervals
        time_slots = [
            (time(10, 0), time(10, 30)),   # 10:00 - 10:30
            (time(10, 30), time(11, 0)),   # 10:30 - 11:00
            (time(11, 0), time(11, 30)),   # 11:00 - 11:30
            (time(11, 30), time(12, 0)),   # 11:30 - 12:00
            (time(12, 0), time(12, 30)),   # 12:00 - 12:30
            (time(12, 30), time(13, 0)),   # 12:30 - 13:00
            (time(13, 0), time(13, 30)),   # 13:00 - 13:30
            (time(13, 30), time(14, 0)),   # 13:30 - 14:00
            (time(14, 0), time(14, 30)),   # 14:00 - 14:30
            (time(14, 30), time(15, 0)),   # 14:30 - 15:00
            (time(15, 0), time(15, 30)),   # 15:30 - 15:30
            (time(15, 30), time(16, 0)),   # 15:30 - 16:00
        ]

        # Days: Sunday (6) to Friday (4) - Python weekday: Monday=0, Sunday=6
        weekdays = [6, 0, 1, 2, 3, 4]  # Sunday to Friday

        # Get all appointment categories
        categories = AppointmentCategory.objects.filter(is_active=True)
        
        if not categories.exists():
            self.stdout.write(self.style.ERROR('No active appointment categories found. Please run setup_appointments first.'))
            return

        # Get users based on their roles and designations
        for category in categories:
            self.stdout.write(f'Setting up slots for category: {category.name}')
            
            # Find users based on category and their designation
            officials = User.objects.none()  # Start with empty queryset
            
            if category.name == 'CAMPUS_CHIEF':
                # Find users with Campus Chief designation
                officials = User.objects.filter(
                    designation__title__icontains='campus chief',
                    is_active=True
                ).exclude(designation__title__icontains='assistant')
            elif category.name == 'ASSISTANT_CAMPUS_CHIEF_ADMIN':
                # Find users with Assistant Campus Chief (Admin) designation
                officials = User.objects.filter(
                    designation__title__icontains='assistant campus chief',
                    is_active=True
                ).filter(designation__title__icontains='admin')
            elif category.name == 'ASSISTANT_CAMPUS_CHIEF_ACADEMIC':
                # Find users with Assistant Campus Chief (Academic) designation
                officials = User.objects.filter(
                    designation__title__icontains='assistant campus chief',
                    is_active=True
                ).filter(designation__title__icontains='academic')
            elif category.name == 'ASSISTANT_CAMPUS_CHIEF_PLANNING':
                # Find users with Assistant Campus Chief (Planning) designation
                officials = User.objects.filter(
                    designation__title__icontains='assistant campus chief',
                    is_active=True
                ).filter(
                    Q(designation__title__icontains='planning') | 
                    Q(designation__title__icontains='resource')
                )
            elif category.name == 'DEPARTMENT_HEAD':
                # Find users with Department Head designation
                officials = User.objects.filter(
                    designation__title__icontains='head',
                    department__isnull=False,
                    is_active=True
                )
            
            if not officials.exists():
                self.stdout.write(f'No officials found for category {category.name}')
                continue
            
            for official in officials:
                self.stdout.write(f'  Creating slots for {official.get_full_name()} ({official.designation.title if official.designation else "No designation"})')
                
                # Create slots for each weekday and time slot
                for weekday in weekdays:
                    for start_time, end_time in time_slots:
                        slot, created = AppointmentSlot.objects.get_or_create(
                            category=category,
                            official=official,
                            weekday=weekday,
                            start_time=start_time,
                            end_time=end_time,
                            defaults={
                                'duration_minutes': 30,
                                'is_active': True,
                                'department': getattr(official, 'department', None)
                            }
                        )
                        
                        if created:
                            self.stdout.write(f'    Created slot: {slot.get_weekday_display()} {start_time} - {end_time}')
        
        self.stdout.write(self.style.SUCCESS('Default appointment slots setup completed!'))