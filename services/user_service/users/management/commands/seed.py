from django.core.management.base import BaseCommand
from users.models import User, SellerProfile, Store
import random


class Command(BaseCommand):
    help = "Seed users and stores"

    def handle(self, *args, **kwargs):

        for i in range(5):
            user = User.objects.create_user(
                username=f"user{i}",
                email=f"user{i}@test.com",
                password="12345678"
            )

            seller = SellerProfile.objects.create(user=user)

            Store.objects.create(
                seller=seller,
                name=f"Store {i}",
                description="Test store",
                wilaya="Algiers",
                city="Bab Ezzouar"
            )

        self.stdout.write(self.style.SUCCESS("Users & Stores seeded!"))