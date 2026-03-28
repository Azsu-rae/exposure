from django.db import models
from django.contrib.auth.models import AbstractUser

import uuid


class User(AbstractUser):
    pass


class Store(models.Model):

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    city = models.CharField(max_length=100)
    # meaning that django automatically sets this field when the object is created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"({self.name}: {self.description} "
            + f"Created at {self.created_at} in {self.city})"
        )


class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    @property
    def in_stock(self):
        return self.stock > 0

    def __str__(self):
        return self.name


class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "Pending"
        CONFIRMED = "Confirmed"
        CANCELLED = "Cancelled"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(
        Product,
        through="OrderItem",
        related_name="orders"
    )

    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()

    @property
    def item_subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in order {self.order.order_id}"
