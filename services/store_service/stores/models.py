from django.db import models
from django.conf import settings
import uuid


# class User(AbstractUser):
#     pass


# class Store(models.Model):
#     owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="stores")
#
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#     city = models.CharField(max_length=100)
#     # meaning that django automatically sets this field when the object is created
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return (
#             f"{self.name}: {self.description}"
#             + f" in {self.city}"
#             + f" and ownned by {self.owner.username}"
#         )


class Product(models.Model):
    store_id = models.ImageField()

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=1)
    image = models.ImageField(upload_to="product_images/", null=True, blank=True)
    is_blocked = models.BooleanField(default=False)

    @property
    def in_stock(self):
        return self.stock > 0

class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "Pending"
        CONFIRMED = "Confirmed"
        CANCELLED = "Cancelled"

    user = models.ImageField()
    products = models.ManyToManyField(
        Product,
        through="OrderItem",
    )

    shipping_address = models.CharField(max_length=255, blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
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
