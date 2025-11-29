# Simple migration to populate appointment_datetime and make it the primary field

from django.db import migrations, models
from django.utils import timezone


def populate_appointment_datetime(apps, schema_editor):
    """Populate appointment_datetime from appointment_date/time where missing"""
    Appointment = apps.get_model('appointments', 'Appointment')
    from datetime import datetime, time
    
    for appointment in Appointment.objects.filter(appointment_datetime__isnull=True):
        if appointment.appointment_date:
            try:
                # Parse time string
                time_str = str(appointment.appointment_time) if appointment.appointment_time else "09:00"
                
                # Handle time formats
                if ':' in time_str:
                    parts = time_str.split(':')
                    hour = int(parts[0])
                    minute = int(parts[1].split()[0]) if len(parts) > 1 else 0
                else:
                    hour = 9
                    minute = 0
                
                # Create timezone-aware datetime
                naive_dt = datetime.combine(appointment.appointment_date, time(hour, minute))
                appointment.appointment_datetime = timezone.make_aware(naive_dt)
                appointment.save(update_fields=['appointment_datetime'])
            except:
                # Default to 9 AM
                naive_dt = datetime.combine(appointment.appointment_date, time(9, 0))
                appointment.appointment_datetime = timezone.make_aware(naive_dt)
                appointment.save(update_fields=['appointment_datetime'])


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0007_add_datetime_field_safe'),
    ]

    operations = [
        # Populate missing appointment_datetime values
        migrations.RunPython(populate_appointment_datetime, migrations.RunPython.noop),
        
        # Make appointment_datetime required
        migrations.AlterField(
            model_name='appointment',
            name='appointment_datetime',
            field=models.DateTimeField(
                help_text='Requested appointment date and time', 
                verbose_name='Appointment Date & Time'
            ),
        ),
    ]