from django.core.management.base import BaseCommand
from stores.messaging import start_consumer


class Command(BaseCommand):
    help = 'Start RabbitMQ event consumer for store_service'

    def handle(self, *args, **options):
        start_consumer()
