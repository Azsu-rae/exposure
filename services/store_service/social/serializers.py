#social/serializers.py
from rest_framework import serializers
from .models import  Post, Review
from stores.models import Product
from stores.serializers import ProductSerializer
from users.serializers import StoreSerializer



class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "user", "stars", "comment", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    page = StoreSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ["id","page", "title", "description", "product", "created_at"]


