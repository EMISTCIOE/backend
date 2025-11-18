#!/usr/bin/env python
"""
Management command to assign programs to staff members based on their responsibilities.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from src.department.models import AcademicProgram
from src.website.models import CampusKeyOfficial


class Command(BaseCommand):
    help = (
        "Assign programs to staff members based on their message/responsibility field"
    )

    # Program mapping based on responsibility keywords
    PROGRAM_MAPPINGS = {
        # Masters Program Coordinators
        "MSEDM": "MMDM",  # MSc. in Mechanical Design and Manufacturing
        "MMDM": "MMDM",
        "MSISE": "MIISE",  # MSc. in Informatics and Intelligent Systems Engineering
        "MIISE": "MIISE",
        "MSEqE": "MEE",  # MSc. in Earthquake Engineering
        "MEE": "MEE",
        "Earthquake": "MEE",
        # Bachelor Programs - Deputy Heads
        "Computer": "BCT",  # Computer Engineering
        "BCT": "BCT",
        "Electronics": "BEI",  # Electronics, Communication and Information
        "BEI": "BEI",
        "Mechanical": "BME",  # Mechanical Engineering
        "BME": "BME",
        "Automobile": "BAM",  # Automobile Engineering
        "BAM": "BAM",
        "Architecture": "BAR",  # Architecture
        "BAR": "BAR",
        "Civil": "BCE",  # Civil Engineering
        "BCE": "BCE",
        "Industrial": "BIE",  # Industrial Engineering
        "BIE": "BIE",
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be updated without making changes",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)

        if dry_run:
            self.stdout.write(
                self.style.WARNING("🔍 DRY RUN MODE - No changes will be made\n"),
            )

        # Get all staff with departments and messages/responsibilities
        staff_with_dept = CampusKeyOfficial.objects.filter(
            department__isnull=False,
        ).exclude(message="")

        self.stdout.write(
            f"📊 Found {staff_with_dept.count()} staff members with departments and messages\n",
        )

        updated_count = 0
        skipped_count = 0

        for staff in staff_with_dept:
            message = staff.message or ""
            responsibility = message.lower()

            # Try to find a program match
            program_short_name = None
            matched_keyword = None

            for keyword, prog_code in self.PROGRAM_MAPPINGS.items():
                if keyword.lower() in responsibility:
                    program_short_name = prog_code
                    matched_keyword = keyword
                    break

            if program_short_name:
                # Find the program
                try:
                    program = AcademicProgram.objects.get(
                        short_name=program_short_name,
                        department=staff.department,
                    )

                    if staff.program != program:
                        self.stdout.write(
                            f"\n✓ {staff.full_name}",
                        )
                        self.stdout.write(
                            f"  Responsibility: {message[:80]}...",
                        )
                        self.stdout.write(
                            f"  Department: {staff.department.short_name}",
                        )
                        self.stdout.write(
                            f"  Matched keyword: '{matched_keyword}' → Program: {program.short_name}",
                        )

                        if not dry_run:
                            with transaction.atomic():
                                staff.program = program
                                staff.save(update_fields=["program", "updated_at"])
                            self.stdout.write(
                                self.style.SUCCESS("  → Updated!"),
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING("  → Would update (dry-run)"),
                            )

                        updated_count += 1
                    else:
                        skipped_count += 1

                except AcademicProgram.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"\n⚠ Program '{program_short_name}' not found for {staff.full_name}",
                        ),
                    )
                except AcademicProgram.MultipleObjectsReturned:
                    self.stdout.write(
                        self.style.ERROR(
                            f"\n✗ Multiple programs found for '{program_short_name}' in {staff.department.short_name}",
                        ),
                    )

        # Print summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("✓ Assignment Complete"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"📊 Total staff checked: {staff_with_dept.count()}")
        self.stdout.write(self.style.SUCCESS(f"✓ Updated: {updated_count}"))
        self.stdout.write(self.style.WARNING(f"⊘ Already assigned: {skipped_count}"))

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\n💡 Run without --dry-run to apply changes",
                ),
            )
