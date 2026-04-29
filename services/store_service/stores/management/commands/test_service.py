
from django.core.management.base import BaseCommand

from stores.services import get_user_id_by_username


class Command(BaseCommand):
    help = "Populate database with sample data (requires user_service to be running)"

    def handle(self, *args, **kwargs):
        user_id = get_user_id_by_username("abdellaoui_mohamed")
        self.stdout.write(f"{user_id=}")
