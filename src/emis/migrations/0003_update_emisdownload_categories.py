from django.db import migrations, models


def forwards(apps, schema_editor):
    EMISDownload = apps.get_model("emis", "EMISDownload")
    # Map legacy categories to new ones
    EMISDownload.objects.filter(category="report_form").update(category="reports")
    EMISDownload.objects.filter(category="resource").update(category="downloads")


def backwards(apps, schema_editor):
    EMISDownload = apps.get_model("emis", "EMISDownload")
    # Best-effort rollback to previous categories
    EMISDownload.objects.filter(category="reports").update(category="report_form")
    EMISDownload.objects.filter(category="downloads").update(category="resource")
    # "forms" has no previous direct mapping; leave as-is


class Migration(migrations.Migration):
    dependencies = [
        ("emis", "0002_emisdownload_emisnotice"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
        migrations.AlterField(
            model_name="emisdownload",
            name="category",
            field=models.CharField(
                choices=[("reports", "Reports"), ("forms", "Forms"), ("downloads", "Downloads")],
                default="downloads",
                max_length=20,
                verbose_name="Category",
            ),
        ),
    ]
