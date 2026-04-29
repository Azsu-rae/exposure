
from django.utils import timezone
from django.db import models
import uuid


class Store(models.Model):

    seller = models.IntegerField()

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    wilaya = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    # meaning?
    is_active = models.BooleanField(default=True)

    # should they be here?
    ccp = models.CharField(max_length=100, blank=True)
    rating = models.FloatField(default=0.0)
#    logo = models.ImageField(
#        upload_to="store_logos/",
#        null=True,
#        blank=True
#    )

    def __str__(self):
        return f"{self.name}"


class Product(models.Model):

    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="products"
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=1)
    category = models.CharField(max_length=100, default='General')

    # here?
    is_blocked = models.BooleanField(default=False)
#    image = models.ImageField(
#        upload_to="product_images/",
#        null=True,
#        blank=True
#    )

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

    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    user = models.IntegerField()
    products = models.ManyToManyField(
        Product,
        through="OrderItem",
    )

    shipping_address = models.CharField(max_length=255, blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
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
        return f"Order by user {self.user} for:{items}\n"


class OrderItem(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    quantity = models.PositiveIntegerField()

    @property
    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
