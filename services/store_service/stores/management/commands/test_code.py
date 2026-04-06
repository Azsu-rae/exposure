
from django.core.management.base import BaseCommand
from stores.models import Product, Store, User


class Command(BaseCommand):
    help = "testing some code"

    def handle(self, *args, **kwargs):
        print(type(Product.objects.all()))

    def iterate(self):
        stores = Store.objects.prefetch_related("product_set")
        for s in stores:
            self.stdout.write(f"\n{s.name}:\n\n")
            products = s.product_set.all()
            for p in products:
                self.stdout.write(f"- {p.name}")

    def create_superuser(self):
        return User.objects.create_superuser(
            username="Ilyas",
            email="aitameurmedilyas@gmail.com",
            password="ilyaspass"
        )
