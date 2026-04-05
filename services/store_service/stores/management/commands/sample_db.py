from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from stores.models import Store, Product, Order, OrderItem


class Command(BaseCommand):
    help = "Populate database with sample data for testing"

    def handle(self, *args, **kwargs):

        user1, user2 = self.sample_users()

        self.stdout.write("Creating stores...")
        stores_data = [
            {"name": "Titanic Coffee", "description": "Expensive coffee shop", "city": "Rouiba"},
            {"name": "Tech Gadgets Hub", "description": "Latest electronics and gadgets", "city": "Algiers"},
            {"name": "Green Grocers", "description": "Fresh organic vegetables and fruits", "city": "Annaba"},
        ]
        stores = []
        for data in stores_data:
            store, _ = Store.objects.get_or_create(name=data["name"], defaults=data)
            stores.append(store)
            self.stdout.write(f"  Created store: {store.name}")

        self.stdout.write("Creating products...")
        products_data = [
            {"store": stores[0], "name": "Espresso", "description": "Strong Italian coffee",
                "price": Decimal("4.50"), "stock": 100},
            {"store": stores[0], "name": "Cappuccino", "description": "Creamy coffee with foam",
                "price": Decimal("6.00"), "stock": 50},
            {"store": stores[0], "name": "Latte", "description": "Smooth coffee with milk",
                "price": Decimal("5.50"), "stock": 75},
            {"store": stores[1], "name": "Wireless Earbuds",
                "description": "Bluetooth 5.0 earbuds", "price": Decimal("49.99"), "stock": 30},
            {"store": stores[1], "name": "Smart Watch", "description": "Fitness tracking smartwatch",
                "price": Decimal("199.99"), "stock": 15},
            {"store": stores[1], "name": "USB-C Hub", "description": "7-in-1 USB-C adapter",
                "price": Decimal("29.99"), "stock": 40},
            {"store": stores[2], "name": "Organic Apples",
                "description": "Fresh red apples (1kg)", "price": Decimal("3.99"), "stock": 200},
            {"store": stores[2], "name": "Avocados",
                "description": "Ripe Hass avocados (pack of 3)", "price": Decimal("5.49"), "stock": 80},
        ]
        products = []
        for data in products_data:
            product, _ = Product.objects.get_or_create(
                name=data["name"],
                store=data["store"],
                defaults={
                    "description": data["description"],
                    "price": data["price"],
                    "stock": data["stock"],
                }
            )
            products.append(product)

        self.stdout.write(f"  Created {len(products)} products")

        self.stdout.write("Creating orders...")
        order1 = Order.objects.create(user=user1, status=Order.StatusChoices.CONFIRMED)
        OrderItem.objects.create(order=order1, product=products[0], quantity=2)
        OrderItem.objects.create(order=order1, product=products[1], quantity=1)

        order2 = Order.objects.create(user=user2, status=Order.StatusChoices.PENDING)
        OrderItem.objects.create(order=order2, product=products[3], quantity=1)
        OrderItem.objects.create(order=order2, product=products[4], quantity=1)

        order3 = Order.objects.create(user=user1, status=Order.StatusChoices.CANCELLED)
        OrderItem.objects.create(order=order3, product=products[6], quantity=5)

        self.stdout.write(self.style.SUCCESS(
            f"Created {Order.objects.count()} orders with {OrderItem.objects.count()} order items"
        ))
        self.stdout.write(self.style.SUCCESS("Sample data populated successfully!"))

    def sample_users(self):
        User = get_user_model()
        from utils.hardcoded import USERS
        users = ()
        self.stdout.write("Creating users...")
        for user in USERS:
            users.append(User.objects.get_or_create(
                username=user["username"],
                defaults=user["profile_infos"]
            )[0])
        self.stdout.write(self.style.SUCCESS(f"Created users: {users}"))

        return users
