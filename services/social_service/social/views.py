from django.db.models import Q
#social/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .services import get_store , get_user , get_product
from .models import  Post, Review

from .serializers import (
    PostSerializer, ReviewSerializer
)


#1. PAGE + POSTS
@api_view(["GET"])
@permission_classes([AllowAny])
def page_api(request, page_id):
    store = get_store(page_id)
    if not store:
        return Response({"error": "Page not found"}, status=404)

    return Response(store)


@api_view(["GET"])
@permission_classes([AllowAny])
def page_posts_api(request, page_id):
    offset = int(request.GET.get("offset", 0))

    posts = Post.objects.filter(store_id=page_id) \
                .order_by("-created_at")[offset:offset + 10]

    result = []
    for post in posts:
        data = PostSerializer(post).data
        data["product"] = get_product(post.product_id)
        result.append(data)

    return Response(result)
# 2. POST DETAIL + REVIEWS
@api_view(["GET"])
@permission_classes([AllowAny])
def post_detail_api(request, post_id):
    post = Post.objects.filter(id=post_id).first()

    if not post:
        return Response({"error": "Post not found"}, status=404)

    post_data = PostSerializer(post).data
    post_data["product"] = get_product(post.product_id)
    post_data["store"] = get_store(post.store_id)

    reviews = Review.objects.filter(post_id=post.id)

    reviews_data = []
    for r in reviews:
        r_data = ReviewSerializer(r).data
        r_data["user"] = get_user(r.user_id)
        reviews_data.append(r_data)

    return Response({
        "post": post_data,
        "reviews": reviews_data
    })

# 3. FEED
# 3. FEED


@api_view(["GET"])
@permission_classes([AllowAny])
def feed(request):
    category = request.GET.get("category")
    search = request.GET.get("search")
    offset = int(request.GET.get("offset", 0))

    posts = Post.objects.all().order_by("-created_at")

    result = []

    for post in posts:
        product = get_product(post.product_id)

        if not product:
            continue

        # filter category
        if category and product.get("category") != category:
            continue

        # filter search
        if search:
            if not (
                search.lower() in post.title.lower()
                or search.lower() in post.description.lower()
                or search.lower() in product.get("name", "").lower()
            ):
                continue

        data = PostSerializer(post).data
        data["product"] = product

        result.append(data)

    return Response(result[offset:offset + 10])

# 4. CREATE POST
@api_view(["POST"])
@permission_classes([AllowAny])
def create_post(request):
    user_id = request.user.id  # من JWT

    product_id = request.data.get("product_id")
    title = request.data.get("title")
    description = request.data.get("description")

    product = get_product(product_id)

    if not product:
        return Response({"error": "Invalid product"}, status=400)

    store_id = product.get("store_id")

    # تحقق أن المستخدم يملك المتجر (اختياري)
    user = get_user(user_id)
    if not user:
        return Response({"error": "Invalid user"}, status=401)

    post = Post.objects.create(
        store_id=store_id,
        product_id=product_id,
        title=title,
        description=description
    )

    return Response(PostSerializer(post).data, status=201)
# 5. ADD REVIEW
@api_view(["POST"])
@permission_classes([AllowAny])
def add_review(request):
    user_id = request.user.id

    post_id = request.data.get("post_id")
    stars = int(request.data.get("stars", 0))
    comment = request.data.get("comment", "")

    if not (1 <= stars <= 5):
        return Response({"error": "Stars must be 1-5"}, status=400)

    post = Post.objects.filter(id=post_id).first()
    if not post:
        return Response({"error": "Post not found"}, status=404)

    if Review.objects.filter(post_id=post_id, user_id=user_id).exists():
        return Response({"error": "Already reviewed"}, status=400)

    review = Review.objects.create(
        post_id=post_id,
        user_id=user_id,
        stars=stars,
        comment=comment
    )

    return Response(ReviewSerializer(review).data)

# 6. GET REVIEWS
@api_view(["GET"])
@permission_classes([AllowAny])
def get_post_reviews(request, post_id):
    offset = int(request.GET.get("offset", 0))

    reviews = Review.objects.filter(post_id=post_id)\
        .order_by("-created_at")[offset:offset + 10]

    result = []
    for r in reviews:
        data = ReviewSerializer(r).data
        data["user"] = get_user(r.user_id)
        result.append(data)

    return Response(result)


