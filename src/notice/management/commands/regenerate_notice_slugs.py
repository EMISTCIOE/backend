from __future__ import annotations

import csv
from typing import Optional

from django.core.management.base import BaseCommand
from django.db import transaction

from src.notice.models import Notice


class Command(BaseCommand):
    help = (
        "Regenerate slugs for Notice objects using the model's slugify().\n"
        "By default this is a dry-run and will only print proposed changes."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--commit",
            action="store_true",
            help="Actually save changes to the database. Without this flag the command only prints proposed updates.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force regeneration for all notices (even if generated slug equals current slug).",
        )
        parser.add_argument(
            "--out-file",
            type=str,
            default=None,
            help="Optional CSV file path to write mapping of old_slug,new_slug,notice_id. (Written only when --commit is used.)",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Optional limit for number of notices to process (0 = no limit).",
        )

    def handle(self, *args, commit: bool = False, force: bool = False, out_file: Optional[str] = None, limit: int = 0, **options):
        qs = Notice.objects.all().order_by("id")
        total = qs.count()
        self.stdout.write(f"Found {total} Notice objects.")

        if limit and limit > 0:
            qs = qs[:limit]

        changes = []
        processed = 0
        updated = 0

        for notice in qs:
            processed += 1
            new_slug = notice.slugify()
            old_slug = notice.slug or ""

            if new_slug == old_slug and not force:
                self.stdout.write(f"{notice.pk}: unchanged")
                continue

            self.stdout.write(f"{notice.pk}: {old_slug} -> {new_slug}")
            changes.append((notice.pk, old_slug, new_slug))

            if commit:
                # Save within a transaction per object to avoid long-running tx
                with transaction.atomic():
                    notice.slug = new_slug
                    notice.save(update_fields=["slug"])
                updated += 1

        self.stdout.write("")
        self.stdout.write(f"Processed: {processed}. Proposed changes: {len(changes)}. Applied: {updated}.")

        if out_file and commit:
            try:
                with open(out_file, "w", newline="", encoding="utf-8") as fh:
                    writer = csv.writer(fh)
                    writer.writerow(["notice_id", "old_slug", "new_slug"])
                    for r in changes:
                        writer.writerow(r)
                self.stdout.write(f"Wrote mapping to {out_file}")
            except Exception as exc:  # pragma: no cover - management convenience
                self.stderr.write(f"Failed to write out file {out_file}: {exc}")

        if not commit:
            self.stdout.write("")
            self.stdout.write("Dry run: no changes applied. Re-run with --commit to persist updates.")
