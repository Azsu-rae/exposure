# #social\models.py

from django.db import models

class Post(models.Model):
    store_id = models.IntegerField()
    product_id = models.IntegerField()

    title = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    post_id = models.IntegerField()
    user_id = models.IntegerField()

    stars = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# from django.core.validators import MinValueValidator, MaxValueValidator
# from django.db import models
# from users.models import User
# from users.models import Store
# from stores.models import Product
#
#
#
# class Post(models.Model):
#     page = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="posts")
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="posts")
#     title = models.CharField(max_length=100)
#     description = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.title
#
#
# class Review(models.Model):
#     post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reviews")
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#
#     stars = models.IntegerField(
#         validators=[MinValueValidator(1), MaxValueValidator(5)]
#     )
#     comment = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"{self.stars}⭐ by {self.user}"
#
# # class Page(models.Model):
# #     name = models.CharField(max_length=20)
# #     bio = models.CharField(max_length=200)
# #     image = models.ImageField(upload_to="profiles/", null=True, blank=True)
# #
# #
# #
# #
# # class Post(models.Model):
# #     title=models.CharField(max_length=30)
# #     description = models.CharField(max_length=255)
# #     price=models.DecimalField(max_digits=8,decimal_places=2)
# #     created_at=models.DateTimeField(auto_now_add=True)
# #     def  __str__(self):
# #        return f"title={self.title} \ndescription={self.description}\nprice={self.price}\ncreated_at={self.created_at} "
# #
# #
# #
# # class Review(models.Model):
# #     post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name="reviews")
# #     stars = models.IntegerField(
# #         validators=[MinValueValidator(1), MaxValueValidator(5)]
# #     )
# #
# #     comment = models.TextField()
# #     created_at = models.DateTimeField(auto_now_add=True)
# #     def __str__(self):
# #         return f"stars={self.stars}\ncomment={self.comment}"
# #
# #     # def validate_stars(self):
# #     #     if self.stars>5:self.stars=0
# #     #     if self.stars<0:self.stars=0
# #
