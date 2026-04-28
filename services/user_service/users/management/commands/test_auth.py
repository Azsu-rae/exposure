from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = "testing authentication"

    def handle(self, *args, **kwargs):
        print(type(User.objects.get(username='abdellaoui_mohamed').password))
