from django.urls import path
from .views import (
    create_post, post_detail, delete_post,
    feed, search_posts, page_detail,
    create_review, delete_review
,health,user)

urlpatterns = [
    # users
    path("users/<int:id>/", user),
    # health
    path("health/", health),
    # 🔵 POSTS
    path("posts/create/", create_post),
    path("posts/<int:post_id>/", post_detail),
    path("posts/<int:post_id>/delete/", delete_post),

    # 🔵 FEED + SEARCH
    path("feed/", feed),
    path("search/", search_posts),

    # 🔵 PAGES (STORE)
    path("pages/<int:store_id>/", page_detail),

    # 🔵 REVIEWS
    path("reviews/create/", create_review),
    path("reviews/<int:review_id>/delete/", delete_review),
]