"""
Management command to sync appointment categories with campus designations.
This creates appointment categories based on active campus staff designations
and ensures the appointment system stays in sync with dynamically created designations.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from src.appointments.models import AppointmentCategory
from src.website.models import CampusStaffDesignation


class Command(BaseCommand):
    help = 'Sync appointment categories with campus designations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreate all categories (will deactivate unused ones)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write("Syncing appointment categories with campus designations...")
        
        # Get active campus designations that allow appointments
        active_designations = CampusStaffDesignation.objects.filter(
            is_active=True, 
            allow_appointments=True
        ).order_by('appointment_priority', 'title')
        
        if not active_designations.exists():
            self.stdout.write(
                self.style.WARNING('No active campus designations with appointment booking enabled found.')
            )
            self.stdout.write('To enable appointments for a designation:')
            self.stdout.write('1. Go to /admin/website/campusstaffdesignation/')
            self.stdout.write('2. Edit the designation')
            self.stdout.write('3. Check "Allow Appointments" checkbox')
            self.stdout.write('4. Set "Appointment Priority" (optional, lower = higher priority)')
            self.stdout.write('5. Save and run this command again')
            return
        
        created_count = 0
        updated_count = 0
        deactivated_count = 0
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made:"))
        
        with transaction.atomic():
            # Create/update categories for active designations
            for designation in active_designations:
                category_name = designation.code
                
                category, created = AppointmentCategory.objects.get_or_create(
                    name=category_name,
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
                    if dry_run:
                        self.stdout.write(f"  Would CREATE: {category_name} -> {designation.title}")
                    else:
                        self.stdout.write(f"  Created: {category_name} -> {designation.title}")
                else:
                    # Update existing category
                    old_description = category.description
                    category.description = f'Appointments with {designation.title}'
                    category.linked_designation = designation
                    category.is_active = True
                    
                    if not dry_run:
                        category.save(update_fields=['description', 'linked_designation', 'is_active'])
                    
                    updated_count += 1
                    if dry_run:
                        self.stdout.write(f"  Would UPDATE: {category_name} -> {designation.title}")
                    else:
                        self.stdout.write(f"  Updated: {category_name} -> {designation.title}")
            
            if force:
                # Deactivate categories that no longer have corresponding designations
                active_designation_codes = list(active_designations.values_list('code', flat=True))
                
                orphaned_categories = AppointmentCategory.objects.filter(
                    is_active=True
                ).exclude(name__in=active_designation_codes)
                
                for category in orphaned_categories:
                    deactivated_count += 1
                    if dry_run:
                        self.stdout.write(f"  Would DEACTIVATE: {category.name} (no matching designation)")
                    else:
                        category.is_active = False
                        category.save(update_fields=['is_active'])
                        self.stdout.write(f"  Deactivated: {category.name} (no matching designation)")
        
        # Summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write("SYNC SUMMARY:")
        self.stdout.write(f"Active designations found: {active_designations.count()}")
        self.stdout.write(f"Categories created: {created_count}")
        self.stdout.write(f"Categories updated: {updated_count}")
        if force:
            self.stdout.write(f"Categories deactivated: {deactivated_count}")
        self.stdout.write("="*60)
        
        if created_count > 0 or updated_count > 0 or deactivated_count > 0:
            if not dry_run:
                self.stdout.write(
                    self.style.SUCCESS("✅ Appointment categories successfully synced!")
                )
            else:
                self.stdout.write(
                    self.style.WARNING("📋 Dry run completed. Use without --dry-run to apply changes.")
                )
        else:
            self.stdout.write(
                self.style.SUCCESS("✅ All appointment categories are already in sync!")
            )
        
        # Show current appointment categories
        self.stdout.write("\nCurrent appointment categories:")
        categories = AppointmentCategory.objects.all().order_by('name')
        for category in categories:
            status = "✅ Active" if category.is_active else "❌ Inactive"
            self.stdout.write(f"  {category.name}: {category.description} [{status}]")