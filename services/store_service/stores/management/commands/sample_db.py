from django.core.management.base import BaseCommand

from stores.utils.hardcoded import STORES, PRODUCTS, ORDERS
from stores.models import Store, Product, Order, OrderItem
from stores.services import get_user_id_by_username


class Command(BaseCommand):
    help = "Populate database with sample data (requires user_service to be running)"

    def handle(self, *args, **kwargs):
        self.sample_stores()
        self.sample_products()
        self.sample_orders()
        self.stdout.write(self.style.SUCCESS("Sample data populated successfully!"))

    def sample_stores(self):
        self.stdout.write("Creating stores...")
        for username, stores_data in STORES.items():
            user_id = get_user_id_by_username(username)
            if not user_id:
                self.stdout.write(self.style.WARNING(f"User '{username}' not found in user_service, skipping."))
                continue
            for store_data in stores_data:
                store, created = Store.objects.get_or_create(
                    name=store_data["name"],
                    defaults={**store_data, "seller": user_id},
                )
                msg = "Created" if created else "Found existing"
                self.stdout.write(self.style.SUCCESS(f"{msg} store: {store}"))

    def sample_products(self):
        self.stdout.write("Creating products...")
        for store_name, products_data in PRODUCTS.items():
            try:
                store = Store.objects.get(name=store_name)
            except Store.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Store '{store_name}' not found, skipping products."))
                continue
            for product_data in products_data:
                product, created = Product.objects.get_or_create(
                    name=product_data["name"],
                    defaults={**product_data, "store": store},
                )
                msg = "Created" if created else "Found existing"
                self.stdout.write(self.style.SUCCESS(f"{msg} product: {product}"))

    def sample_orders(self):
        self.stdout.write("Creating orders...")
        for username, orders_data in ORDERS.items():
            user_id = get_user_id_by_username(username)
            if not user_id:
                self.stdout.write(self.style.WARNING(f"User '{username}' not found in user_service, skipping."))
                continue
            for order_data in orders_data:
                order = Order.objects.create(
                    user=user_id,
                    status=order_data["status"],
                )
                for item_data in order_data.get("items", []):
                    try:
                        product = Product.objects.get(name=item_data["product"])
                        OrderItem.objects.create(order=order, product=product, quantity=item_data["quantity"])
                    except Product.DoesNotExist:
                        self.stdout.write(self.style.WARNING(
                            f"Product '{item_data['product']}' not found, skipping item."))
                self.stdout.write(self.style.SUCCESS(f"Created order: {order}"))
