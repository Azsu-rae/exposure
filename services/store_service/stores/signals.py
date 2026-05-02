from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from stores.models import Order, Product, Store


# --- Stores -------------------------------------------------------------

@receiver(post_save, sender=Store)
def on_store_saved(sender, instance, created, **kwargs):
    from stores.messaging import publish_store_created, publish_store_updated
    publisher = publish_store_created if created else publish_store_updated
    transaction.on_commit(lambda: publisher(instance))


@receiver(post_delete, sender=Store)
def on_store_deleted(sender, instance, **kwargs):
    from stores.messaging import publish_store_deleted
    store_id = instance.id
    transaction.on_commit(lambda: publish_store_deleted(store_id))


# --- Products -----------------------------------------------------------

@receiver(post_save, sender=Product)
def on_product_saved(sender, instance, created, **kwargs):
    from stores.messaging import publish_product_created, publish_product_updated
    publisher = publish_product_created if created else publish_product_updated
    transaction.on_commit(lambda: publisher(instance))


@receiver(post_delete, sender=Product)
def on_product_deleted(sender, instance, **kwargs):
    from stores.messaging import publish_product_deleted
    product_id = instance.id
    transaction.on_commit(lambda: publish_product_deleted(product_id))


# --- Orders -------------------------------------------------------------

@receiver(post_save, sender=Order)
def on_order_created(sender, instance, created, **kwargs):
    if not created:
        return
    from stores.messaging import publish_order_created
    transaction.on_commit(lambda: publish_order_created(instance))
