from django.db import models


class Payment(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING"
        HELD = "HELD"
        RELEASED = "RELEASED"
        REFUNDED = "REFUNDED"
        FAILED = "FAILED"

    class Method(models.TextChoices):
        CASH = "CASH"
        CARD = "CARD"

    order_id = models.UUIDField(unique=True)
    seller_id = models.IntegerField()
    buyer_id = models.IntegerField()

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=Method.choices)

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )

    checkout_url = models.URLField(null=True, blank=True)
    release_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} ({self.method}) - {self.status}"
