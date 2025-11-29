"""
Management command to enable appointments for key campus designations.
This command identifies and enables appointment booking for:
- Campus Chief
- Assistant Campus Chiefs (all types)
- Department/HOD roles
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from src.website.models import CampusStaffDesignation


class Command(BaseCommand):
    help = 'Enable appointments for key campus designations (Campus Chief, Assistant Chiefs, HODs)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be enabled without making changes',
        )
        parser.add_argument(
            '--custom',
            nargs='*',
            help='Enable appointments for custom designation codes (space-separated)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        custom_codes = options.get('custom', [])
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made"))
        
        self.stdout.write("Enabling appointments for key designations...")
        
        # Define key designation patterns that should have appointments
        key_patterns = [
            'campus_chief',
            'campus_cheif',  # Handle typo in your data
            'assistant_campus_chief',
            'hod',
            'department_head',
            'head_of_department',
        ]
        
        # Add custom codes if provided
        if custom_codes:
            key_patterns.extend([code.lower() for code in custom_codes])
        
        updated_count = 0
        enabled_designations = []
        
        with transaction.atomic():
            all_designations = CampusStaffDesignation.objects.filter(is_active=True)
            
            for designation in all_designations:
                should_enable = any(
                    pattern in designation.code.lower() or 
                    pattern in designation.title.lower() 
                    for pattern in key_patterns
                )
                
                if should_enable and not designation.allow_appointments:
                    if not dry_run:
                        designation.allow_appointments = True
                        
                        # Set priority based on role
                        if 'campus_chief' in designation.code.lower() or 'campus_cheif' in designation.code.lower():
                            if 'assistant' not in designation.code.lower():
                                designation.appointment_priority = 1  # Campus Chief highest priority
                            else:
                                designation.appointment_priority = 2  # Assistant Chiefs
                        elif 'hod' in designation.code.lower() or 'department' in designation.code.lower():
                            designation.appointment_priority = 3  # Department heads
                        else:
                            designation.appointment_priority = 4  # Others
                        
                        designation.save(update_fields=['allow_appointments', 'appointment_priority'])
                    
                    updated_count += 1
                    enabled_designations.append(designation)
                    
                    if dry_run:
                        self.stdout.write(f"  Would ENABLE: {designation.code} -> {designation.title}")
                    else:
                        self.stdout.write(f"  ✅ ENABLED: {designation.code} -> {designation.title}")
        
        # Show summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write("SUMMARY:")
        self.stdout.write(f"Designations processed: {all_designations.count()}")
        self.stdout.write(f"Appointments enabled for: {updated_count}")
        
        if enabled_designations:
            self.stdout.write("\nDesignations now enabled for appointments:")
            for designation in enabled_designations:
                priority = designation.appointment_priority or "No priority"
                self.stdout.write(f"  • {designation.title} (Code: {designation.code}) [Priority: {priority}]")
        
        self.stdout.write("="*60)
        
        if updated_count > 0:
            if not dry_run:
                self.stdout.write(
                    self.style.SUCCESS("✅ Appointment booking enabled for key designations!")
                )
                self.stdout.write("\nNext steps:")
                self.stdout.write("1. Run: python manage.py sync_appointment_categories")
                self.stdout.write("2. Run: python manage.py setup_appointments")
            else:
                self.stdout.write(
                    self.style.WARNING("📋 Dry run completed. Use without --dry-run to apply changes.")
                )
        else:
            self.stdout.write(
                self.style.SUCCESS("✅ All key designations already have appointments enabled!")
            )