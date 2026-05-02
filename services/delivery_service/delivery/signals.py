from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from delivery.models import Delivery


@receiver(pre_save, sender=Delivery)
def track_previous_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._previous_status = Delivery.objects.get(pk=instance.pk).delivery_status
        except Delivery.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=Delivery)
def on_delivery_status_changed(sender, instance, created, **kwargs):
    if created or instance.delivery_status == getattr(instance, '_previous_status', None):
        return
    from delivery.messaging import publish_delivery_status_changed
    transaction.on_commit(lambda: publish_delivery_status_changed(instance))
