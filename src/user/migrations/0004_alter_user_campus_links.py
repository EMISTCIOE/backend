from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0033_merge_20251119_1437"),
        ("user", "0003_user_campus_section_user_campus_unit_alter_user_role"),
    ]

    operations = [
        migrations.AlterField(
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
        migrations.AlterField(
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
    ]
