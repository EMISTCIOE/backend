from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0034_campusfeedback_resolved_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="campuskeyofficial",
            name="campus_section",
            field=models.ForeignKey(
                blank=True,
                help_text="Campus section the staff member is associated with (if applicable).",
                null=True,
                on_delete=models.SET_NULL,
                related_name="staff_members_primary",
                to="website.campussection",
                verbose_name="Campus Section",
            ),
        ),
    ]
