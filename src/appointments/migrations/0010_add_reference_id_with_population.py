# Custom migration to add reference_id field with data population

from django.db import migrations, models
import string
import random


def populate_reference_ids(apps, schema_editor):
    """Populate reference_id for existing appointments"""
    Appointment = apps.get_model('appointments', 'Appointment')
    
    for appointment in Appointment.objects.all():
        while True:
            # Generate 5-character alphanumeric code (mixed case + numbers)
            reference_id = ''.join(random.choices(
                string.ascii_lowercase + string.ascii_uppercase + string.digits, k=5
            ))
            # Check if this reference_id already exists
            if not Appointment.objects.filter(reference_id=reference_id).exists():
                appointment.reference_id = reference_id
                appointment.save(update_fields=['reference_id'])
                break


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0009_remove_old_fields_final'),
    ]

    operations = [
        # Step 1: Add the field without unique constraint first
        migrations.AddField(
            model_name='appointment',
            name='reference_id',
            field=models.CharField(blank=True, help_text='Unique 5-character appointment reference ID', max_length=10, verbose_name='Reference ID'),
        ),
        
        # Step 2: Populate existing records
        migrations.RunPython(populate_reference_ids, migrations.RunPython.noop),
        
        # Step 3: Add unique constraint
        migrations.AlterField(
            model_name='appointment',
            name='reference_id',
            field=models.CharField(blank=True, help_text='Unique 5-character appointment reference ID', max_length=10, unique=True, verbose_name='Reference ID'),
        ),
    ]