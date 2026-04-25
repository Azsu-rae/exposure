from rest_framework import serializers
from .models import Page, Post, Review


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Review
        fields = ["id", "user", "stars", "comment", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "description",
            "price",
            "image",
            "created_at",
            "reviews"
        ]


class PageSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True, read_only=True)

    class Meta:
        model = Page
        fields = [
            "id",
            "name",
            "bio",
            "image",
            "posts"
        ]