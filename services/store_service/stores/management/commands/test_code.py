
from django.core.management.base import BaseCommand
from stores.models import Product, Store, User, Order


class Command(BaseCommand):
    help = "testing some code"

    def handle(self, *args, **kwargs):
        pass

    def reverse_relations(self):
        print(User.objects.get(username="abdellaoui_mohamed").store_set.all())
        print(Order.objects.filter(user=1)[0].items.all())
        print(Product.objects.get(name="Smart Watch").items.all()[0])

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
