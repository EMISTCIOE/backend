from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import HomePage, Unit, Resource, Report, ImageGallery


@receiver(pre_delete, sender=HomePage)
def delete_homepage(sender, instance, **kwargs):
    instance.slider_image1.delete()
    instance.slider_image2.delete()
    instance.slider_image3.delete()
    instance.slider_image4.delete()
    instance.video.delete()


@receiver(pre_delete, sender=Unit)
def delete_unit(sender, instance, **kwargs):
    instance.image.delete()


@receiver(pre_delete, sender=Resource)
def delete_resource(sender, instance, **kwargs):
    instance.image.delete()
    instance.file.delete()


@receiver(pre_delete, sender=Report)
def delete_report(sender, instance, **kwargs):
    instance.file.delete()


@receiver(pre_delete, sender=ImageGallery)
def delete_image(sender, instance, **kwargs):
    # delete all images in the gallery
    for image in instance.image_set.all():
        image.image.delete()
