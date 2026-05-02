from django.core.management.base import BaseCommand

from social.messaging import start_consumer


class Command(BaseCommand):
    help = 'Start RabbitMQ event consumer for social_service'

    def handle(self, *args, **options):
        start_consumer()
