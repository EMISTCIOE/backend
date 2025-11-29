# Generated migration to make appointment categories dynamic

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0004_alter_appointmentcategory_name'),  # Update this to your latest migration
    ]

    operations = [
        # Remove the hardcoded choices constraint
        migrations.AlterField(
            model_name='appointmentcategory',
            name='name',
            field=models.CharField(
                help_text='Category name that maps to campus designation codes',
                max_length=150,  # Increased to match CampusStaffDesignation code field
                unique=True,
                verbose_name='Category Name'
            ),
        ),
        
        # Add a field to link to campus designation (optional for backward compatibility)
        migrations.AddField(
            model_name='appointmentcategory',
            name='linked_designation',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name='appointment_categories',
                to='website.campusStaffDesignation',
                help_text='Campus designation this category is linked to (optional)',
                verbose_name='Linked Designation'
            ),
        ),
        
        # Add fields for better appointment management
        migrations.AddField(
            model_name='appointmentcategory',
            name='default_duration_minutes',
            field=models.PositiveIntegerField(
                default=30,
                help_text='Default duration for appointments in this category',
                verbose_name='Default Duration (minutes)'
            ),
        ),
        
        migrations.AddField(
            model_name='appointmentcategory',
            name='advance_booking_days',
            field=models.PositiveIntegerField(
                default=7,
                help_text='How many days in advance appointments can be booked',
                verbose_name='Advance Booking Days'
            ),
        ),
        
        migrations.AddField(
            model_name='appointmentcategory',
            name='requires_approval',
            field=models.BooleanField(
                default=True,
                help_text='Whether appointments in this category require admin approval',
                verbose_name='Requires Approval'
            ),
        ),
    ]