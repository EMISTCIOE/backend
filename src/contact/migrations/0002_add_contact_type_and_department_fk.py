# Generated manually for better data migration
from django.db import migrations, models
import django.db.models.deletion


def migrate_existing_data(apps, schema_editor):
    """
    Migrate existing phone number data to the new structure.
    - Copy department_name to name field
    - Set appropriate contact_type based on department_name
    """
    PhoneNumber = apps.get_model('contact', 'PhoneNumber')
    Department = apps.get_model('department', 'Department')
    
    # Mapping of department names to determine contact type
    campus_keywords = ['campus', 'main']
    section_keywords = ['admin', 'account', 'store', 'library', 'emis', 'exam']
    
    for phone in PhoneNumber.objects.all():
        # Copy department_name to name
        phone.name = phone.department_name_temp
        
        # Determine contact type
        name_lower = phone.name.lower()
        
        if any(keyword in name_lower for keyword in campus_keywords):
            phone.contact_type = 'campus'
        elif any(keyword in name_lower for keyword in section_keywords):
            phone.contact_type = 'section'
        else:
            # Try to find matching department
            phone.contact_type = 'department'
            # Look for department by name similarity
            try:
                dept = Department.objects.filter(name__icontains=phone.name.split()[0]).first()
                if dept:
                    phone.department = dept
                    phone.name = dept.name
            except:
                # If no match found, keep as section
                phone.contact_type = 'section'
        
        phone.save()


class Migration(migrations.Migration):

    dependencies = [
        ('department', '0009_departmentevent_location_and_more'),
        ('contact', '0001_initial'),
    ]

    operations = [
        # Step 0: Update model options first to use temp ordering
        migrations.AlterModelOptions(
            name='phonenumber',
            options={
                'ordering': ['display_order', 'id'],  # Temporary safe ordering
                'verbose_name': 'Phone Number',
                'verbose_name_plural': 'Phone Numbers',
            },
        ),
        
        # Step 1: Rename department_name to a temp field
        migrations.RenameField(
            model_name='phonenumber',
            old_name='department_name',
            new_name='department_name_temp',
        ),
        
        # Step 2: Add new fields with nullable/defaults
        migrations.AddField(
            model_name='phonenumber',
            name='contact_type',
            field=models.CharField(
                choices=[
                    ('campus', 'Campus'),
                    ('department', 'Department'),
                    ('section', 'Section/Unit'),
                ],
                default='section',
                help_text='Type of contact: Campus, Department, or Section/Unit',
                max_length=20,
                verbose_name='Contact Type',
            ),
        ),
        migrations.AddField(
            model_name='phonenumber',
            name='department',
            field=models.ForeignKey(
                blank=True,
                help_text='Link to Department (only for department type contacts)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='contact_numbers',
                to='department.department',
                verbose_name='Department',
            ),
        ),
        migrations.AddField(
            model_name='phonenumber',
            name='name',
            field=models.CharField(
                help_text="Name of the contact (e.g., 'Main Campus', 'Civil Department', 'Library')",
                max_length=100,
                verbose_name='Contact Name',
                default='',  # Temporary default
            ),
            preserve_default=False,
        ),
        
        # Step 3: Migrate existing data
        migrations.RunPython(migrate_existing_data, reverse_code=migrations.RunPython.noop),
        
        # Step 4: Remove temp field
        migrations.RemoveField(
            model_name='phonenumber',
            name='department_name_temp',
        ),
        
        # Step 5: Update model options with final ordering
        migrations.AlterModelOptions(
            name='phonenumber',
            options={
                'ordering': ['display_order', 'name'],
                'verbose_name': 'Phone Number',
                'verbose_name_plural': 'Phone Numbers',
            },
        ),
        migrations.AddIndex(
            model_name='phonenumber',
            index=models.Index(
                fields=['contact_type', 'is_active'],
                name='contact_pho_contact_fe0d2c_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='phonenumber',
            index=models.Index(
                fields=['department', 'is_active'],
                name='contact_pho_departm_640754_idx',
            ),
        ),
    ]
