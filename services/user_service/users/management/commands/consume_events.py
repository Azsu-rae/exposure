from django.core.management.base import BaseCommand
from users.messaging import start_consumer


class Command(BaseCommand):
    help = 'Start RabbitMQ event consumer for user_service'

    def handle(self, *args, **options):
        start_consumer()
