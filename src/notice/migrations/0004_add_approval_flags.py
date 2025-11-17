"""Add approval boolean flags to Notice

Generated migration to add is_approved_by_department and is_approved_by_campus.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notice", "0003_alter_notice_department"),
    ]

    operations = [
        migrations.AddField(
            model_name="notice",
            name="is_approved_by_department",
            field=models.BooleanField(default=False, verbose_name="Approved by Department"),
        ),
        migrations.AddField(
            model_name="notice",
            name="is_approved_by_campus",
            field=models.BooleanField(default=False, verbose_name="Approved by Campus"),
        ),
    ]
