from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Notice


@receiver(pre_delete, sender=Notice)
def delete_notice(sender, instance, **kwargs):
    instance.thumbnail.delete()
    instance.download_file.delete()
