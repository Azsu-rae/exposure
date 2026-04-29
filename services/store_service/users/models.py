# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    # ── fields every user has (buyer behaviour) ──────────────────────────
    email = models.EmailField(unique=True)
    phone           = models.CharField(max_length=20, unique=True, null=True, blank=True)
    profile_picture = models.ImageField(upload_to="profiles/", null=True, blank=True)
    wilaya          = models.CharField(max_length=100, blank=True)
    address         = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    # ── seller activation ─────────────────────────────────────────────────
    is_activated = models.BooleanField(default=False)  # completed seller form?
    active_mode  = models.CharField(
        max_length=10,
        choices=[("BUYER", "Buyer"), ("SELLER", "Seller")],
        default="BUYER"
    )

    def __str__(self):
        return self.username

    # every user can buy — no check needed
    # seller actions are gated by is_activated
    @property
    def is_seller_mode(self):
        return self.is_activated and self.active_mode == "SELLER"

    def activate_seller(self):
        self.is_activated = True
        self.active_mode  = "SELLER"
        self.save(update_fields=["is_activated", "active_mode"])

    def switch_mode(self):
        if not self.is_activated:
            raise ValueError("Complete seller registration first.")
        self.active_mode = "BUYER" if self.active_mode == "SELLER" else "SELLER"
        self.save(update_fields=["active_mode"])


class BuyerProfile(models.Model):
    """
    Extra buyer-specific fields.
    Created automatically on register via signal.
    Every user has this — even sellers.
    """
    user            = models.OneToOneField(User, on_delete=models.CASCADE,
                                           related_name="buyer_profile")
    default_wilaya  = models.CharField(max_length=100, blank=True)
    default_address = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"Buyer: {self.user.username}"


class SellerProfile(models.Model):
    """
    Created only when user completes the activation form.
    Has Store nested inside it — one seller, one store.
    """
    user        = models.OneToOneField(User, on_delete=models.CASCADE,
                                       related_name="seller_profile")
    bio         = models.TextField(blank=True)
    id_document = models.ImageField(upload_to="seller_docs/", null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    balance     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rating      = models.FloatField(default=0.0)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"Seller: {self.user.username}"


class Store(models.Model):
    """
    Lives inside users app — belongs to a SellerProfile.
    Access from anywhere: user.seller_profile.store
    """
    seller      = models.OneToOneField(SellerProfile, on_delete=models.CASCADE,
                                       related_name="store")
    # seller = models.ForeignKey(
    #     SellerProfile,
    #     on_delete=models.CASCADE,
    #     related_name="stores"
    # )
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    logo        = models.ImageField(upload_to="store_logos/", null=True, blank=True)
    wilaya      = models.CharField(max_length=100)
    city        = models.CharField(max_length=100)
    ccp = models.CharField(max_length=100, blank=True)
    is_active   = models.BooleanField(default=True)
    rating      = models.FloatField(default=0.0)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"{self.name} — {self.seller.user.username}"