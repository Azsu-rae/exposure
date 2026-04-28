from django.db import models
from django.utils import timezone
from .services import transfer_to_seller

class Payment(models.Model):

    class Status(models.TextChoices):
        PENDING  = "PENDING"
        PAID     = "PAID"
        FAILED   = "FAILED"
        # CANCELED = "CANCELED"
        # EXPIRED  = "EXPIRED"
        HELD     = "HELD"
        RELEASED = "RELEASED"
        REFUNDED = "REFUNDED"
        PAID_OUT = "PAID_OUT"

    class Method(models.TextChoices):
        CASH = "CASH"
        CARD = "CARD"

    order_id     = models.UUIDField()
    amount       = models.IntegerField()
    method       = models.CharField(         # ← NEW
        max_length=10,
        choices=Method.choices,
        default=Method.CARD,
    )

    entity_id    = models.CharField(max_length=100, unique=True, null=True, blank=True)
    checkout_url = models.URLField(null=True, blank=True)

    status       = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )

    release_date = models.DateTimeField(null=True, blank=True)  # ← NEW

    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} ({self.method}) - {self.status}"

    def mark_paid(self):
        self.status = self.Status.HELD
        self.save()

    def mark_failed(self):
        self.status = self.Status.FAILED
        self.save()

    def mark_released(self):
        try:
            transfer_to_seller(
                chargily_id=self.seller.chargily_id,
                amount=self.seller_amount,
            )
        except Exception as e:
            # don't change status — payment stays HELD
            # log the error so you can investigate
            raise Exception(f"Transfer failed, payment stays HELD: {str(e)}")

        self.status = self.Status.RELEASED
        self.release_date = timezone.now()
        self.save()

        self.seller.balance += self.seller_amount
        self.seller.save()

    def mark_refunded(self):                 # ← NEW
        self.status = self.Status.REFUNDED
        self.save()