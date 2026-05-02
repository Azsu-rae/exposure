from django.core.management.base import BaseCommand

from payment.messaging import start_consumer


class Command(BaseCommand):
    help = 'Start RabbitMQ event consumer for payment_service'

    def handle(self, *args, **options):
        start_consumer()
