from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import User


@receiver(post_save, sender=User)
def on_user_saved(sender, instance, created, **kwargs):
    from .messaging import publish_user_created, publish_user_updated
    publisher = publish_user_created if created else publish_user_updated
    transaction.on_commit(lambda: publisher(instance))


@receiver(post_delete, sender=User)
def on_user_deleted(sender, instance, **kwargs):
    from .messaging import publish_user_deleted
    user_id = instance.id
    transaction.on_commit(lambda: publish_user_deleted(user_id))
