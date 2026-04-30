from django.db.models.signals import post_save
from django.dispatch import receiver
from stores.models import Order, Store


@receiver(post_save, sender=Store)
def on_store_created(sender, instance, created, **kwargs):
    if created:
        from stores.messaging import publish_store_created
        publish_store_created(instance)


@receiver(post_save, sender=Order)
def on_order_created(sender, instance, created, **kwargs):
    if created:
        from stores.messaging import publish_order_created
        publish_order_created(instance)
