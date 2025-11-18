"""
Signal handlers for synchronizing phone numbers between Department and PhoneNumber models.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from src.contact.models import ContactType, PhoneNumber
from src.department.models import Department


@receiver(post_save, sender=Department)
def sync_department_phone_to_contact(sender, instance, created, **kwargs):
    """
    When a Department's phone_no is updated, sync it to the associated PhoneNumber record.
    Creates a new PhoneNumber if one doesn't exist for this department and it has a phone number.
    If phone_no is empty, the PhoneNumber won't be shown in public API.
    """
    # Avoid recursion by checking if signal is already being processed
    if hasattr(instance, "_syncing_phone"):
        return

    # If department has a phone number, create or update the PhoneNumber record
    if instance.phone_no:
        # Find or create the associated PhoneNumber
        phone_record, created = PhoneNumber.objects.get_or_create(
            department=instance,
            contact_type=ContactType.DEPARTMENT,
            defaults={
                "name": instance.name,
                "phone_number": instance.phone_no,
                "description": f"Main contact for {instance.name}",
                "display_order": 100,  # Default order for department contacts
                "created_by": instance.updated_by or instance.created_by,
            },
        )

        # Update existing record if phone number or name changed
        if not created:
            needs_update = False
            if phone_record.phone_number != instance.phone_no:
                phone_record.phone_number = instance.phone_no
                needs_update = True
            if phone_record.name != instance.name:
                phone_record.name = instance.name
                needs_update = True

            if needs_update:
                phone_record._syncing_phone = True
                phone_record.updated_by = instance.updated_by
                phone_record.save()
                if hasattr(phone_record, "_syncing_phone"):
                    delattr(phone_record, "_syncing_phone")
    else:
        # If department has no phone number, deactivate any existing PhoneNumber
        PhoneNumber.objects.filter(
            department=instance,
            contact_type=ContactType.DEPARTMENT,
        ).update(is_active=False)


@receiver(pre_save, sender=PhoneNumber)
def sync_contact_phone_to_department(sender, instance, **kwargs):
    """
    When a PhoneNumber linked to a Department is updated, sync it back to the Department.
    Only syncs if contact_type is DEPARTMENT.
    """
    if instance.contact_type != ContactType.DEPARTMENT or not instance.department:
        return

    # Avoid recursion
    if hasattr(instance, "_syncing_phone"):
        return

    # Update the department's phone number if it changed
    if instance.department.phone_no != instance.phone_number:
        instance.department._syncing_phone = True
        instance.department.phone_no = instance.phone_number
        instance.department.updated_by = instance.updated_by
        instance.department.save()
        if hasattr(instance.department, "_syncing_phone"):
            delattr(instance.department, "_syncing_phone")

    # Ensure name stays in sync with department
    if instance.name != instance.department.name:
        instance.name = instance.department.name
