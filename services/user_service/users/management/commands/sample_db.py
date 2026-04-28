from django.core.management import BaseCommand
from users.utils import hardcoded
from users.models import User


class Command(BaseCommand):
    help = "Populate database with sample data for testing"

    def handle(self, *args, **kwards):
        self.stdout.write("Creating users...")
        for user_data in hardcoded.USERS:
            password = user_data.pop("password", None)
            user, created = User.objects.get_or_create(
                username=user_data["username"],
                defaults=user_data,
            )
            if created and password:
                user.set_password(password)
                user.save()
