from django.core.management.base import BaseCommand
from delivery.messaging import start_consumer


class Command(BaseCommand):
    help = 'Start RabbitMQ event consumer for delivery_service'

    def handle(self, *args, **options):
        start_consumer()
