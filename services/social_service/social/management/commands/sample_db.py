from django.core.management.base import BaseCommand

from social.utils.hardcoded import POSTS, REVIEWS
from social.models import Post, Review, UserRef, StoreRef, ProductRef


class Command(BaseCommand):
    help = "Populate database with sample data (requires consume_events to have populated UserRef/StoreRef/ProductRef)"

    def handle(self, *args, **kwargs):
        self.sample_posts()
        self.sample_reviews()
        self.stdout.write(self.style.SUCCESS("Sample data populated successfully!"))

    def sample_posts(self):
        self.stdout.write("Creating posts...")
        for post_data in POSTS:
            try:
                store = StoreRef.objects.get(name=post_data["store_name"])
            except StoreRef.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f"Store '{post_data['store_name']}' not in local refs, skipping post."))
                continue
            try:
                product = ProductRef.objects.get(name=post_data["product_name"], store_id=store.id)
            except ProductRef.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f"Product '{post_data['product_name']}' not in local refs, skipping post."))
                continue
            post, created = Post.objects.get_or_create(
                title=post_data["title"],
                defaults={
                    "store_id": store.id,
                    "product_id": product.id,
                    "description": post_data["description"],
                    "category": post_data["category"],
                },
            )
            msg = "Created" if created else "Found existing"
            self.stdout.write(self.style.SUCCESS(f"{msg} post: {post.title}"))

    def sample_reviews(self):
        self.stdout.write("Creating reviews...")
        for review_data in REVIEWS:
            try:
                post = Post.objects.get(title=review_data["post_title"])
            except Post.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f"Post '{review_data['post_title']}' not found, skipping review."))
                continue
            try:
                user = UserRef.objects.get(username=review_data["username"])
            except UserRef.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f"User '{review_data['username']}' not in local refs, skipping review."))
                continue
            review, created = Review.objects.get_or_create(
                post=post,
                user_id=user.id,
                defaults={
                    "stars": review_data["stars"],
                    "comment": review_data["comment"],
                },
            )
            msg = "Created" if created else "Found existing"
            self.stdout.write(self.style.SUCCESS(f"{msg} review: {review.stars}* on {post.title}"))
