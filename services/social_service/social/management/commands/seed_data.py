from django.core.management.base import BaseCommand
from social.models import Page, Post, Review
from users.models import User


class Command(BaseCommand):
    help = "Seed database with pages, posts, and reviews"

    def handle(self, *args, **kwargs):

        # 🔹 create or get user
        user, _ = User.objects.get_or_create(
            username="testuser",
            email="qw@gm.com",
            defaults={"password": "1234"}
        )

        # 🔹 create page
        page = Page.objects.create(
            owner=user,
            name="Demo Store",
            bio="This is a demo store"
        )

        self.stdout.write(self.style.SUCCESS("Page created"))

        # 🔹 create posts
        for i in range(3):
            post = Post.objects.create(
                page=page,
                title=f"Product {i}",
                description="Test product",
                price=100 + i
            )

            self.stdout.write(self.style.SUCCESS(f"Post {i} created"))

            # 🔹 create reviews
            for s in [3, 4, 5]:
                Review.objects.create(
                    post=post,
                    user=user,
                    stars=s,
                    comment=f"Review with {s} stars"
                )

        self.stdout.write(self.style.SUCCESS("Seeding done"))