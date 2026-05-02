from rest_framework import serializers

from .models import Post, Review, UserRef, StoreRef, ProductRef


class UserRefSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRef
        fields = ['id', 'username', 'role']


class StoreRefSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreRef
        fields = ['id', 'name', 'wilaya', 'city', 'rating']


class ProductRefSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRef
        fields = ['id', 'store_id', 'name', 'price', 'category']


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'store_id', 'product_id', 'category',
                  'title', 'description', 'image', 'created_at']
        read_only_fields = ['id', 'store_id', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'post', 'user_id', 'stars', 'comment', 'created_at']
        read_only_fields = ['id', 'user_id', 'created_at']
