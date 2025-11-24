"""
Management command to approve notices by setting approval flags and status.

Usage:
    python manage.py approve_notices              # Approve all pending/draft notices
    python manage.py approve_notices --all        # Approve all notices regardless of status
    python manage.py approve_notices --ids 1 2 3  # Approve specific notice IDs
    python manage.py approve_notices --slug notice-title-2024  # Approve by slug
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from src.notice.constants import NoticeStatus
from src.notice.models import Notice


class Command(BaseCommand):
    help = "Approve notices by setting approval flags and status to APPROVED"

    def add_arguments(self, parser):
        parser.add_argument(
            "--ids",
            nargs="+",
            type=int,
            help="Specific notice IDs to approve",
        )
        parser.add_argument(
            "--slug",
            type=str,
            help="Approve a notice by its slug",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Approve all notices regardless of current status",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be approved without making changes",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        notice_ids = options.get("ids")
        notice_slug = options.get("slug")
        approve_all = options.get("all", False)

        # Build the queryset based on options
        if notice_ids:
            queryset = Notice.objects.filter(id__in=notice_ids)
            self.stdout.write(f"Targeting {len(notice_ids)} notice(s) by ID...")
        elif notice_slug:
            queryset = Notice.objects.filter(slug=notice_slug)
            self.stdout.write(f"Targeting notice with slug: {notice_slug}")
        elif approve_all:
            queryset = Notice.objects.all()
            self.stdout.write("Targeting ALL notices...")
        else:
            # Default: approve only PENDING and DRAFT notices
            queryset = Notice.objects.filter(
                status__in=[NoticeStatus.PENDING.value, NoticeStatus.DRAFT.value],
            )
            self.stdout.write("Targeting PENDING and DRAFT notices...")

        # Filter only non-archived and active notices
        queryset = queryset.filter(is_archived=False, is_active=True)

        count = queryset.count()
        if count == 0:
            self.stdout.write(
                self.style.WARNING("No notices found matching the criteria."),
            )
            return

        self.stdout.write(f"\nFound {count} notice(s) to approve:")
        for notice in queryset:
            dept_status = "✓" if notice.is_approved_by_department else "✗"
            campus_status = "✓" if notice.is_approved_by_campus else "✗"
            self.stdout.write(
                f"  - ID: {notice.id} | {notice.title[:50]} | "
                f"Status: {notice.status} | "
                f"Dept: {dept_status} | Campus: {campus_status}",
            )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\n[DRY RUN] No changes made. Remove --dry-run to apply changes.",
                ),
            )
            return

        # Confirm before proceeding
        confirm = input(
            f"\nAre you sure you want to approve these {count} notice(s)? [y/N]: ",
        )
        if confirm.lower() not in ["y", "yes"]:
            self.stdout.write(self.style.WARNING("Operation cancelled."))
            return

        # Perform the approval
        try:
            with transaction.atomic():
                updated_count = queryset.update(
                    is_approved_by_department=True,
                    is_approved_by_campus=True,
                    status=NoticeStatus.APPROVED.value,
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✓ Successfully approved {updated_count} notice(s)!",
                ),
            )

            # Show updated status
            self.stdout.write("\nUpdated notices:")
            for notice in queryset:
                notice.refresh_from_db()
                self.stdout.write(
                    f"  ✓ ID: {notice.id} | {notice.title[:50]} | "
                    f"Status: {notice.status} | "
                    f"Dept: ✓ | Campus: ✓",
                )

        except Exception as e:
            raise CommandError(f"Error approving notices: {e!s}")
