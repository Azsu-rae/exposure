# management/commands/seeder.py

import json
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.db import transaction

from users.models import User, SellerProfile, Store
from stores.models import Product
from social.models import Post, Review


class Command(BaseCommand):
    help = "Seed database from JSON file"

    def handle(self, *args, **kwargs):
        with open("seed_data.json") as f:
            data = json.load(f)

        with transaction.atomic():

            self.stdout.write(self.style.WARNING("Deleting old data..."))

            Review.objects.all().delete()
            Post.objects.all().delete()
            Product.objects.all().delete()
            Store.objects.all().delete()
            SellerProfile.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

            # ─────────────────────────────
            # USERS
            # ─────────────────────────────
            self.stdout.write(self.style.WARNING("Creating users..."))

            user_map = {}

            for u in data["users"]:
                user = User.objects.create(
                    username=u["username"],
                    email=u["email"],
                    password=make_password(u["password"]),
                    wilaya=u.get("wilaya", ""),
                    address=u.get("address", "")
                )

                user_map[user.username] = user

                if u.get("is_seller"):
                    # activate seller first
                    user.is_activated = True
                    user.active_mode = "SELLER"
                    user.save(update_fields=["is_activated", "active_mode"])

                    # then create seller profile
                    SellerProfile.objects.create(user=user)

            # ─────────────────────────────
            # STORES
            # ─────────────────────────────
            self.stdout.write(self.style.WARNING("Creating stores..."))

            store_map = {}

            for s in data["stores"]:
                user = user_map.get(s["owner"])

                if not user:
                    self.stdout.write(self.style.ERROR(f"User {s['owner']} not found"))
                    continue

                if not hasattr(user, "seller_profile"):
                    self.stdout.write(self.style.ERROR(f"{user.username} is not a seller"))
                    continue

                store = Store.objects.create(
                    seller=user.seller_profile,
                    name=s["name"],
                    description=s.get("description", ""),
                    wilaya=s["wilaya"],
                    city=s["city"]
                )

                store_map[store.name] = store

            # ─────────────────────────────
            # PRODUCTS
            # ─────────────────────────────
            self.stdout.write(self.style.WARNING("Creating products..."))

            product_map = {}

            for p in data["products"]:
                store = store_map.get(p["store"])

                if not store:
                    self.stdout.write(self.style.ERROR(f"Store {p['store']} not found"))
                    continue

                product = Product.objects.create(
                    store=store,
                    name=p["name"],
                    description=p.get("description", ""),
                    price=p["price"],
                    stock=p["stock"],
                    category=p["category"]
                )

                product_map[product.name] = product

            # ─────────────────────────────
            # POSTS
            # ─────────────────────────────
            self.stdout.write(self.style.WARNING("Creating posts..."))

            post_map = {}

            for p in data["posts"]:
                product = product_map.get(p["product"])

                if not product:
                    self.stdout.write(self.style.ERROR(f"Product {p['product']} not found"))
                    continue

                post = Post.objects.create(
                    page=product.store,
                    product=product,
                    title=p["title"],
                    description=p["description"]
                )

                post_map[post.title] = post

            # ─────────────────────────────
            # REVIEWS
            # ─────────────────────────────
            self.stdout.write(self.style.WARNING("Creating reviews..."))

            for r in data["reviews"]:
                post = post_map.get(r["post"])
                user = user_map.get(r["user"])

                if not post:
                    self.stdout.write(self.style.ERROR(f"Post {r['post']} not found"))
                    continue

                if not user:
                    self.stdout.write(self.style.ERROR(f"User {r['user']} not found"))
                    continue

                Review.objects.create(
                    post=post,
                    user=user,
                    stars=r["stars"],
                    comment=r["comment"]
                )

            self.stdout.write(self.style.SUCCESS("✅ Data seeded successfully"))