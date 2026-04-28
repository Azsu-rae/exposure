# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        BUYER = "BUYER"
        SELLER = "SELLER"
        DELIVERY = "DELIVERY"
        ADMIN = "ADMIN"

    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.BUYER
    )

    # username
    # password
    # there, hashed
    # automatically
    # email
    # first_name
    # last_name
    # is_active
    # is_staff
    # is_superuser
    # date_joined
    # last_login
    # groups
    # user_permissions

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_seller(self):
        return self.role == self.Role.SELLER

    @property
    def is_buyer(self):
        return self.role == self.Role.BUYER

    @property
    def is_delivery(self):
        return self.role == self.Role.DELIVERY


class SellerProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="seller_profile"
    )

    store_name = models.CharField(max_length=255)
    chargily_id = models.CharField(max_length=100, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.store_name


class DeliveryProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="delivery_profile"
    )

    company_name = models.CharField(max_length=255)
    wilaya = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.company_name
