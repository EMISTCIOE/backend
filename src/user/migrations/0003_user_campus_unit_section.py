from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0002_user_classification_fields"),
        ("website", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="campus_section",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="user_campus_sections",
                to="website.campussection",
                verbose_name="campus section",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="campus_unit",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="user_campus_units",
                to="website.campusunit",
                verbose_name="campus unit",
            ),
        ),
    ]
