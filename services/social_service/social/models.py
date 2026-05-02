from django.db import models


class Post(models.Model):
    store_id = models.IntegerField(db_index=True)
    product_id = models.IntegerField(db_index=True)
    image = models.ImageField(upload_to="posts_images/", null=True, blank=True)
    category = models.CharField(max_length=100, db_index=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reviews')
    user_id = models.IntegerField(db_index=True)
    stars = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('post', 'user_id')]


# --- Event-replicated read models ----------------------------------------
# These tables are populated by RabbitMQ consumers from user_service and
# store_service events. They are denormalised projections of the source
# of truth — never written by the social_service business logic itself.

class UserRef(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=150)
    role = models.CharField(max_length=20)
    updated_at = models.DateTimeField(auto_now=True)


class StoreRef(models.Model):
    id = models.IntegerField(primary_key=True)
    seller_id = models.IntegerField(db_index=True)
    name = models.CharField(max_length=100)
    wilaya = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    rating = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)


class ProductRef(models.Model):
    id = models.IntegerField(primary_key=True)
    store_id = models.IntegerField(db_index=True)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, default='General')
    updated_at = models.DateTimeField(auto_now=True)
