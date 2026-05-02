"""
All cross-service joins happen against locally-replicated read models
(UserRef, StoreRef, ProductRef) populated by the RabbitMQ consumer in
social.messaging. The service makes no synchronous HTTP calls to other
services — it only depends on the broker.
"""

from django.db.models import Avg, Count, Q
from django.http import JsonResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Post, Review, UserRef, StoreRef, ProductRef
from .serializers import (
    PostSerializer, ReviewSerializer,
    UserRefSerializer, StoreRefSerializer, ProductRefSerializer,
)
from .permissions import IsSeller


@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    return JsonResponse({'status': 'ok'})


# ---------------- Posts ---------------------------------------------------

def _enrich_posts(posts):
    """Bulk-load product+store from local refs once, then map by id."""
    product_ids = {p.product_id for p in posts}
    store_ids = {p.store_id for p in posts}
    products = {p.id: p for p in ProductRef.objects.filter(id__in=product_ids)}
    stores = {s.id: s for s in StoreRef.objects.filter(id__in=store_ids)}

    result = []
    for post in posts:
        data = PostSerializer(post).data
        prod = products.get(post.product_id)
        store = stores.get(post.store_id)
        data['product'] = ProductRefSerializer(prod).data if prod else None
        data['store'] = StoreRefSerializer(store).data if store else None
        data['avg_rating'] = round(getattr(post, 'avg_rating', 0) or 0, 2)
        result.append(data)
    return result


@api_view(['POST'])
@permission_classes([IsSeller])
def create_post(request):
    product_id = request.data.get('product_id')
    if not product_id:
        return Response({'error': 'product_id is required.'}, status=400)

    try:
        product = ProductRef.objects.get(id=product_id)
    except ProductRef.DoesNotExist:
        return Response({'error': 'Unknown product.'}, status=400)

    try:
        store = StoreRef.objects.get(id=product.store_id)
    except StoreRef.DoesNotExist:
        return Response({'error': 'Store missing for this product.'}, status=400)

    if store.seller_id != request.user.id:
        return Response({'error': 'You can only post for your own store.'}, status=403)

    post = Post.objects.create(
        store_id=store.id,
        product_id=product.id,
        title=request.data.get('title', ''),
        description=request.data.get('description', ''),
        category=request.data.get('category', product.category),
        image=request.FILES.get('image'),
    )
    return Response(PostSerializer(post).data, status=201)


@api_view(['GET'])
@permission_classes([AllowAny])
def post_detail(request, post_id):
    post = Post.objects.filter(id=post_id).annotate(
        avg_rating=Avg('reviews__stars')
    ).first()
    if not post:
        return Response({'error': 'Post not found.'}, status=404)

    enriched = _enrich_posts([post])[0]

    reviews = list(post.reviews.all())
    user_ids = {r.user_id for r in reviews}
    users = {u.id: u for u in UserRef.objects.filter(id__in=user_ids)}

    reviews_data = []
    for r in reviews:
        data = ReviewSerializer(r).data
        u = users.get(r.user_id)
        data['user'] = UserRefSerializer(u).data if u else None
        reviews_data.append(data)

    stats = post.reviews.aggregate(avg=Avg('stars'), count=Count('id'))
    enriched['avg_rating'] = round(stats['avg'], 2) if stats['avg'] else 0
    enriched['reviews_count'] = stats['count']
    enriched['reviews'] = reviews_data
    return Response(enriched)


@api_view(['DELETE'])
@permission_classes([IsSeller])
def delete_post(request, post_id):
    post = Post.objects.filter(id=post_id).first()
    if not post:
        return Response({'error': 'Post not found.'}, status=404)

    store = StoreRef.objects.filter(id=post.store_id).first()
    if not store or store.seller_id != request.user.id:
        return Response({'error': 'Unauthorized.'}, status=403)

    post.delete()
    return Response({'message': 'Post deleted.'})


@api_view(['GET'])
@permission_classes([AllowAny])
def feed(request):
    category = request.GET.get('category')
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 10))

    qs = Post.objects.annotate(avg_rating=Avg('reviews__stars')).order_by('-created_at')
    if category:
        qs = qs.filter(category=category)
    posts = list(qs[offset:offset + limit])
    return Response(_enrich_posts(posts))


@api_view(['GET'])
@permission_classes([AllowAny])
def search_posts(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category')

    qs = Post.objects.annotate(avg_rating=Avg('reviews__stars'))
    if query:
        qs = qs.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category:
        qs = qs.filter(category=category)

    posts = list(qs[:10])
    return Response(_enrich_posts(posts))


# ---------------- Pages ---------------------------------------------------

@api_view(['GET'])
@permission_classes([AllowAny])
def page_detail(request, store_id):
    store = StoreRef.objects.filter(id=store_id).first()
    if not store:
        return Response({'error': 'Store not found.'}, status=404)

    posts = list(
        Post.objects.filter(store_id=store_id)
        .annotate(avg_rating=Avg('reviews__stars'))
        .order_by('-created_at')
    )
    post_ids = [p.id for p in posts]
    stats = Review.objects.filter(post_id__in=post_ids).aggregate(
        avg=Avg('stars'), count=Count('id')
    )
    return Response({
        'store': StoreRefSerializer(store).data,
        'store_avg_rating': round(stats['avg'], 2) if stats['avg'] else 0,
        'store_reviews_count': stats['count'],
        'posts': _enrich_posts(posts),
    })


# ---------------- Reviews -------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request):
    post_id = request.data.get('post_id')
    stars = request.data.get('stars')
    comment = request.data.get('comment', '')

    try:
        stars = int(stars)
    except (TypeError, ValueError):
        return Response({'error': 'stars must be an integer 1-5.'}, status=400)
    if not (1 <= stars <= 5):
        return Response({'error': 'stars must be between 1 and 5.'}, status=400)

    post = Post.objects.filter(id=post_id).first()
    if not post:
        return Response({'error': 'Post not found.'}, status=404)

    if Review.objects.filter(post=post, user_id=request.user.id).exists():
        return Response({'error': 'You already reviewed this post.'}, status=400)

    review = Review.objects.create(
        post=post,
        user_id=request.user.id,
        stars=stars,
        comment=comment,
    )
    return Response(ReviewSerializer(review).data, status=201)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, review_id):
    review = Review.objects.filter(id=review_id).first()
    if not review:
        return Response({'error': 'Review not found.'}, status=404)
    if review.user_id != request.user.id:
        return Response({'error': 'Unauthorized.'}, status=403)
    review.delete()
    return Response({'message': 'Review deleted.'})
