# Generated manually for new user classification fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0001_initial"),
        ("department", "0001_initial"),
        ("website", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("EMIS-STAFF", "EMIS Staff"),
                    ("ADMIN", "Admin"),
                    ("DEPARTMENT-ADMIN", "Department Admin"),
                    ("CLUB", "Student Club"),
                    ("UNION", "Union"),
                ],
                default="EMIS-STAFF",
                max_length=32,
                verbose_name="role",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="designation",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="users",
                to="website.campusstaffdesignation",
                verbose_name="designation",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="department",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="users",
                to="department.department",
                verbose_name="department",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="club",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="user_clubs",
                to="website.studentclub",
                verbose_name="student club",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="union",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="user_unions",
                to="website.campusunion",
                verbose_name="union",
            ),
        ),
    ]
