from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from stores.utils.hardcoded import USERS, STORES, PRODUCTS, ORDERS
from stores.models import Store, Product, Order, OrderItem

User = get_user_model()


class Command(BaseCommand):
    help = "Populate database with sample data for testing"

    def handle(self, *args, **kwargs):
        self.sample_users()
        self.sample_stores()
        self.sample_products()
        self.sample_orders()
        self.stdout.write(self.style.SUCCESS("Sample data populated successfully!"))

    def sample_users(self):
        self.stdout.write("Creating users...")
        for user_data in USERS:
            user, created = User.objects.get_or_create(
                username=user_data["username"],
                defaults=user_data
            )
            msg = "Created" if created else "Found existing"
            self.stdout.write(self.style.SUCCESS(f"{msg} user: {user}"))

    def sample_stores(self):
        self.stdout.write("Creating stores...")
        for owner, stores_data in STORES.items():
            user = User.objects.get(username=owner)
            for store_data in stores_data:
                store_data["owner"] = user
                store, created = Store.objects.get_or_create(
                    name=store_data["name"],
                    defaults=store_data
                )
                msg = "Created" if created else "Found existing"
                self.stdout.write(self.style.SUCCESS(f"{msg} store: {store}"))

    def sample_products(self):
        self.stdout.write("Creating products...")
        for store_name, products_data in PRODUCTS.items():
            store = Store.objects.get(name=store_name)
            for product_data in products_data:
                product_data["store"] = store
                product, created = Product.objects.get_or_create(
                    name=product_data["name"],
                    defaults=product_data
                )
                msg = "Created" if created else "Found existing"
                self.stdout.write(self.style.SUCCESS(f"{msg} product: {product}"))

    def sample_orders(self):
        self.stdout.write("Creating orders...")
        for username, orders_data in ORDERS.items():
            user = User.objects.get(username=username)
            for order_data in orders_data:
                order = Order.objects.create(
                    user=user,
                    status=order_data["status"]
                )
                for item_data in order_data.get("items", []):
                    product = Product.objects.get(name=item_data["product"])
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item_data["quantity"]
                    )
                self.stdout.write(self.style.SUCCESS(f"Created order: {order}"))
