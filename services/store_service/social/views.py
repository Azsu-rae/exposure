#social/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from users.models import Store
from users.serializers import StoreSerializer

from .models import  Post, Review
from stores.models import Product
from .serializers import (
    PostSerializer, ReviewSerializer
)


#1. PAGE + POSTS
@api_view(["GET"])
@permission_classes([AllowAny])
def page_api(request, page_id):
    page = Store.objects.filter(id=page_id).first()
    if not page:
        return Response({"error": "Page not found"}, status=404)

    serializer = StoreSerializer(page)
    return Response(serializer.data)

from django.db.models import Q

@api_view(["GET"])
@permission_classes([AllowAny])
def page_posts_api(request, page_id):
    offset = int(request.GET.get("offset", 0))
    posts = Post.objects.filter(page_id=page_id).order_by("-created_at")[offset:offset + 10]
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

# 2. POST DETAIL + REVIEWS
@api_view(["GET"])
@permission_classes([AllowAny])
def post_detail_api(request, post_id):
    post = Post.objects.filter(id=post_id).first()
    if not post:
        return Response({"error": "Post not found"}, status=404)

    post_data = PostSerializer(post).data
    reviews = ReviewSerializer(post.reviews.all(), many=True).data

    return Response({
        "post": post_data,
        "reviews": reviews
    })


# 3. FEED
# 3. FEED
from django.db.models import Q


@api_view(["GET"])
@permission_classes([AllowAny])
def feed(request):
    category = request.GET.get("category")
    search = request.GET.get("search")
    offset = int(request.GET.get("offset", 0))

    queryset = Post.objects.all()

    if category:
        queryset = queryset.filter(product__category=category)

    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(product__name__icontains=search)
        )

    posts = queryset.order_by("-created_at")[offset:offset + 10]

    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)


# 4. CREATE POST
@api_view(["POST"])
@permission_classes([AllowAny])
def create_post(request):
    user = request.user

    if not user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)

    # store_id = request.data.get("store_id")
    product_id = request.data.get("product_id")
    title = request.data.get("title")
    description = request.data.get("description")
    store = user.seller_profile

    #  check product belongs to this store
    product = Product.objects.filter(id=product_id, store=store).first()
    if not product:
        return Response({"error": "Product not in your store"}, status=403)

    # create post
    post = Post.objects.create(
        page=store,
        product=product,
        title=title,
        description=description
    )

    serializer = PostSerializer(post)
    return Response(serializer.data, status=201)

# 5. ADD REVIEW
@api_view(["POST"])
@permission_classes([AllowAny])
def add_review(request):
    user = request.user

    if not user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)

    post_id = request.data.get("post_id")
    stars = int(request.data.get("stars", 0))
    comment = request.data.get("comment", "")

    if not (1 <= stars <= 5):
        return Response({"error": "Stars must be 1-5"}, status=400)

    post = Post.objects.filter(id=post_id).first()
    if not post:
        return Response({"error": "Post not found"}, status=404)

    if Review.objects.filter(post=post, user=user).exists():
        return Response({"error": "Already reviewed"}, status=400)

    review = Review.objects.create(
        post=post,
        user=user,
        stars=stars,
        comment=comment
    )

    serializer = ReviewSerializer(review)
    return Response(serializer.data)


# 6. GET REVIEWS
@api_view(["GET"])
@permission_classes([AllowAny])
def get_post_reviews(request, post_id):
    offset = int(request.GET.get("offset", 0))

    reviews = Review.objects.filter(post_id=post_id)\
        .order_by("-created_at")[offset:offset + 10]

    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)