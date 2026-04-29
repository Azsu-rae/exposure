import random
from django.db.models import Avg, Count, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .services import get_store, get_user, get_product, get_users_bulk, get_products_bulk , get_stores_bulk
from .models import Post, Review
from .serializers import PostSerializer, ReviewSerializer

########################### Posts ######################################

@api_view(["POST"])
@permission_classes([IsAuthenticated]) # Changed from AllowAny
def create_post(request):
    user_id = request.user.id

    product_id = request.data.get("product_id")
    title = request.data.get("title")
    description = request.data.get("description")
    category = request.data.get("category")
    image = request.FILES.get("image")

    product = get_product(product_id)
    if not product:
        return Response({"error": "Invalid product"}, status=400)

    store_id = product.get("store_id")

    post = Post.objects.create(
        store_id=store_id,
        product_id=product_id,
        title=title,
        description=description,
        category=category,
        image=image
    )

    return Response(PostSerializer(post).data, status=201)

@api_view(["GET"])
@permission_classes([AllowAny])
def post_detail(request, post_id):
    post = Post.objects.filter(id=post_id).first()
    if not post:
        return Response({"error": "Post not found"}, status=404)

    post_data = PostSerializer(post).data
    post_data["product"] = get_product(post.product_id)

    store = get_store(post.store_id)

    reviews = Review.objects.filter(post_id=post.id)
    avg = reviews.aggregate(avg=Avg("stars"), count=Count("id"))

    # Bulk fetch users for the reviews
    user_ids = [r.user_id for r in reviews]
    users_map = get_users_bulk(user_ids)

    reviews_data = []
    for r in reviews:
        r_data = ReviewSerializer(r).data
        r_data["user"] = users_map.get(r.user_id) # Mapped from memory
        reviews_data.append(r_data)

    return Response({
        "post": post_data,
        "store_name": store.get("name") if store else None,
        "avg_rating": round(avg["avg"], 2) if avg["avg"] else 0,
        "reviews_count": avg["count"],
        "reviews": reviews_data
    })

@api_view(["DELETE"])
@permission_classes([IsAuthenticated]) # Added proper auth
def delete_post(request, post_id):
    post = Post.objects.filter(id=post_id).first()

    if not post:
        return Response({"error": "Post not found"}, status=404)

    # Note: Assuming user.id == store_id in your architecture
    if post.store_id != request.user.id:
        return Response({"error": "Unauthorized"}, status=403)

    post.delete()
    return Response({"message": "Post deleted"})


@api_view(["GET"])
@permission_classes([AllowAny])
def feed(request):
    category = request.GET.get("category")
    offset = int(request.GET.get("offset", 0))
    limit = 10

    posts_qs = Post.objects.annotate(avg_rating=Avg('review__stars')).order_by("-created_at")

    if category:
        cat_posts = list(posts_qs.filter(category=category)[offset:offset + 5])
        other_posts = list(posts_qs.exclude(category=category)[offset:offset + 5])
        selected = cat_posts + other_posts
        random.shuffle(selected)
    else:
        selected = list(posts_qs[offset:offset + limit])

    # 1. Collect all IDs for bulk calls
    product_ids = [p.product_id for p in selected]
    store_ids = [p.store_id for p in selected]

    # 2. Fetch data from other services in bulk
    products_map = get_products_bulk(product_ids)
    stores_map = get_stores_bulk(store_ids)

    result = []
    for post in selected:
        data = PostSerializer(post).data

        # 3. Map the external data back to the post
        data["product"] = products_map.get(post.product_id)
        data["store"] = stores_map.get(post.store_id)  # Adds name and logo
        data["avg_rating"] = round(post.avg_rating, 2) if post.avg_rating else 0

        result.append(data)

    return Response(result)
@api_view(["GET"])
@permission_classes([AllowAny])
def search_posts(request):
    query = request.GET.get("q", "")
    category = request.GET.get("category")

    posts_qs = Post.objects.annotate(avg_rating=Avg('review__stars'))

    if query:
        posts_qs = posts_qs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    if category:
        posts_qs = posts_qs.filter(category=category)

    selected = posts_qs[:10]

    result = []
    for post in selected:
        data = PostSerializer(post).data
        data["avg_rating"] = round(post.avg_rating, 2) if post.avg_rating else 0
        result.append(data)

    return Response(result)

################################# Pages #######################

@api_view(["GET"])
@permission_classes([AllowAny])
def page_detail(request, store_id):
    store = get_store(store_id)
    if not store:
        return Response({"error": "Store not found"}, status=404)

    # Annotate again to avoid the inner loop DB hits
    posts = Post.objects.filter(store_id=store_id).annotate(avg_rating=Avg('review__stars'))
    all_post_ids = posts.values_list("id", flat=True)

    store_stats = Review.objects.filter(post_id__in=all_post_ids).aggregate(
        avg=Avg("stars"),
        count=Count("id")
    )

    result_posts = []
    for post in posts:
        data = PostSerializer(post).data
        data["avg_rating"] = round(post.avg_rating, 2) if post.avg_rating else 0
        result_posts.append(data)

    return Response({
        "store": store,
        "store_avg_rating": round(store_stats["avg"], 2) if store_stats["avg"] else 0,
        "store_reviews_count": store_stats["count"],
        "posts": result_posts
    })

############################ Reviews ########################

@api_view(["POST"])
@permission_classes([IsAuthenticated]) # Added proper auth
def create_review(request):
    user_id = request.user.id

    post_id = request.data.get("post_id")
    stars = request.data.get("stars")
    comment = request.data.get("comment", "")

    if stars is None or not (1 <= int(stars) <= 5):
        return Response({"error": "Invalid stars"}, status=400)

    if Review.objects.filter(post_id=post_id, user_id=user_id).exists():
        return Response({"error": "Already reviewed"}, status=400)

    review = Review.objects.create(
        post_id=post_id,
        user_id=user_id,
        stars=int(stars),
        comment=comment
    )

    return Response(ReviewSerializer(review).data, status=201)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated]) # Added proper auth
def delete_review(request, review_id):
    review = Review.objects.filter(id=review_id).first()

    if not review:
        return Response({"error": "Review not found"}, status=404)

    if review.user_id != request.user.id:
        return Response({"error": "Unauthorized"}, status=403)

    review.delete()
    return Response({"message": "Review deleted"})


#
# #1. PAGE + POSTS
# @api_view(["GET"])
# @permission_classes([AllowAny])
# def page_api(request, page_id):
#     store = get_store(page_id)
#     if not store:
#         return Response({"error": "Page not found"}, status=404)
#
#     return Response(store)
#
#
# @api_view(["GET"])
# @permission_classes([AllowAny])
# def page_posts_api(request, page_id):
#     offset = int(request.GET.get("offset", 0))
#
#     posts = Post.objects.filter(store_id=page_id) \
#                 .order_by("-created_at")[offset:offset + 10]
#
#     result = []
#     for post in posts:
#         data = PostSerializer(post).data
#         data["product"] = get_product(post.product_id)
#         result.append(data)
#
#     return Response(result)
# # 2. POST DETAIL + REVIEWS
# @api_view(["GET"])
# @permission_classes([AllowAny])
# def post_detail_api(request, post_id):
#     post = Post.objects.filter(id=post_id).first()
#
#     if not post:
#         return Response({"error": "Post not found"}, status=404)
#
#     post_data = PostSerializer(post).data
#     post_data["product"] = get_product(post.product_id)
#     post_data["store"] = get_store(post.store_id)
#
#     reviews = Review.objects.filter(post_id=post.id)
#
#     reviews_data = []
#     for r in reviews:
#         r_data = ReviewSerializer(r).data
#         r_data["user"] = get_user(r.user_id)
#         reviews_data.append(r_data)
#
#     return Response({
#         "post": post_data,
#         "reviews": reviews_data
#     })
#
# # 3. FEED
# # 3. FEED
#
#
# @api_view(["GET"])
# @permission_classes([AllowAny])
# def feed(request):
#     category = request.GET.get("category")
#     search = request.GET.get("search")
#     offset = int(request.GET.get("offset", 0))
#
#     posts = Post.objects.all().order_by("-created_at")
#
#     result = []
#
#     for post in posts:
#         product = get_product(post.product_id)
#
#         if not product:
#             continue
#
#         # filter category
#         if category and product.get("category") != category:
#             continue
#
#         # filter search
#         if search:
#             if not (
#                 search.lower() in post.title.lower()
#                 or search.lower() in post.description.lower()
#                 or search.lower() in product.get("name", "").lower()
#             ):
#                 continue
#
#         data = PostSerializer(post).data
#         data["product"] = product
#
#         result.append(data)
#
#     return Response(result[offset:offset + 10])
#
# # 4. CREATE POST
# @api_view(["POST"])
# @permission_classes([AllowAny])
# def create_post(request):
#     user_id = request.user.id
#     product_id = request.data.get("product_id")
#     title = request.data.get("title")
#     description = request.data.get("description")
#
#     product = get_product(product_id)
#
#     if not product:
#         return Response({"error": "Invalid product"}, status=400)
#
#     store_id = product.get("store_id")
#
#
#     user = get_user(user_id)
#     if not user:
#         return Response({"error": "Invalid user"}, status=401)
#
#     post = Post.objects.create(
#         store_id=store_id,
#         product_id=product_id,
#         title=title,
#         description=description
#     )
#
#     return Response(PostSerializer(post).data, status=201)
# # 5. ADD REVIEW
# @api_view(["POST"])
# @permission_classes([AllowAny])
# def add_review(request):
#     user_id = request.user.id
#
#     post_id = request.data.get("post_id")
#     stars = int(request.data.get("stars", 0))
#     comment = request.data.get("comment", "")
#
#     if not (1 <= stars <= 5):
#         return Response({"error": "Stars must be 1-5"}, status=400)
#
#     post = Post.objects.filter(id=post_id).first()
#     if not post:
#         return Response({"error": "Post not found"}, status=404)
#
#     if Review.objects.filter(post_id=post_id, user_id=user_id).exists():
#         return Response({"error": "Already reviewed"}, status=400)
#
#     review = Review.objects.create(
#         post_id=post_id,
#         user_id=user_id,
#         stars=stars,
#         comment=comment
#     )
#
#     return Response(ReviewSerializer(review).data)
#
# # 6. GET REVIEWS
# @api_view(["GET"])
# @permission_classes([AllowAny])
# def get_post_reviews(request, post_id):
#     offset = int(request.GET.get("offset", 0))
#
#     reviews = Review.objects.filter(post_id=post_id)\
#         .order_by("-created_at")[offset:offset + 10]
#
#     result = []
#     for r in reviews:
#         data = ReviewSerializer(r).data
#         data["user"] = get_user(r.user_id)
#         result.append(data)
#
#     return Response(result)
#
# # mean for a post
# from django.db.models import Avg, Count
#
# @api_view(["GET"])
# @permission_classes([AllowAny])
# def get_post_rating_avg(request, post_id):
#     stats = Review.objects.filter(post_id=post_id).aggregate(
#         avg_stars=Avg("stars"),
#         total_reviews=Count("id")
#     )
#
#     return Response({
#         "post_id": post_id,
#         "average": round(stats["avg_stars"], 2) if stats["avg_stars"] else 0,
#         "count": stats["total_reviews"]
#     })
#
# @api_view(["GET"])
# @permission_classes([AllowAny])
# def get_store_rating_avg(request, store_id):
#     post_ids = Post.objects.filter(store_id=store_id).values_list("id", flat=True)
#
#     stats = Review.objects.filter(post_id__in=post_ids).aggregate(
#         avg_stars=Avg("stars"),
#         total_reviews=Count("id")
#     )
#
#     return Response({
#         "store_id": store_id,
#         "average": round(stats["avg_stars"], 2) if stats["avg_stars"] else 0,
#         "count": stats["total_reviews"]
#     })