from django.urls import path

from . import views

urlpatterns = [
    path('social/health/', views.health),

    # posts
    path('posts/', views.feed),
    path('posts/create/', views.create_post),
    path('posts/<int:post_id>/', views.post_detail),
    path('posts/<int:post_id>/delete/', views.delete_post),

    # search
    path('search/', views.search_posts),

    # pages
    path('pages/<int:store_id>/', views.page_detail),

    # reviews
    path('reviews/create/', views.create_review),
    path('reviews/<int:review_id>/delete/', views.delete_review),
]
