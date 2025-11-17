"""Add approval boolean flags to GlobalEvent

Generated migration to add is_approved_by_department and is_approved_by_campus.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0026_globalgalleryimage_section_globalgalleryimage_unit_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="globalevent",
            name="is_approved_by_department",
            field=models.BooleanField(default=False, verbose_name="Approved by Department"),
        ),
        migrations.AddField(
            model_name="globalevent",
            name="is_approved_by_campus",
            field=models.BooleanField(default=False, verbose_name="Approved by Campus"),
        ),
    ]
