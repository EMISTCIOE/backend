from django.db import migrations, models
from django.utils.text import slugify


def generate_slugs(apps, schema_editor):
    Project = apps.get_model("project", "Project")

    for project in Project.objects.all():
        base_slug = slugify(project.slug or project.title) or "project"
        candidate = base_slug
        counter = 2

        while (
            Project.objects.filter(slug=candidate)
            .exclude(pk=project.pk)
            .exists()
        ):
            candidate = f"{base_slug}-{counter}"
            counter += 1

        project.slug = candidate
        project.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [
        ("project", "0002_project_academic_program"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text="URL-friendly identifier for the project",
                max_length=255,
                null=True,
                unique=True,
                verbose_name="Slug",
            ),
        ),
        migrations.RunPython(generate_slugs, migrations.RunPython.noop),
    ]
