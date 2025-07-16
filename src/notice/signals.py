import os
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Notice


def safe_delete_file(file_field):
    """
    Deletes a file from storage only if it exists and is not reused.
    """
    if file_field and hasattr(file_field, "path"):
        file_path = file_field.path
        if os.path.isfile(file_path):
            try:
                file_field.delete(save=False)
            except Exception as e:
                pass


@receiver(pre_delete, sender=Notice)
def delete_notice_files(sender, instance: Notice, **kwargs):
    safe_delete_file(instance.thumbnail)
    safe_delete_file(instance.download_file)
