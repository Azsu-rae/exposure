from django.db import models

from django.conf import settings
import uuid


class Store(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="stores")

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    city = models.CharField(max_length=100)
    # meaning that django automatically sets this field when the object is created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.name}: {self.description}"
            + f" in {self.city}"
            + f" and ownned by {self.owner.username}"
        )


class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    @property
    def in_stock(self):
        return self.stock > 0

    def __str__(self):
        return f"{self.name} available at {self.store.name}"


class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "Pending"
        CONFIRMED = "Confirmed"
        CANCELLED = "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ← instead of direct User import
        on_delete=models.CASCADE
    )
    products = models.ManyToManyField(
        Product,
        through="OrderItem",
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )

    def __str__(self):

        items = ""
        for item in self.items.all():
            items += f"\n* {item}"

        return f"Order by {self.user.username} for:{items}\n"


class OrderItem(models.Model):
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()

    @property
    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
