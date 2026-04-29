from django.urls import path
from . import views

urlpatterns = [
    # Page + its posts
    path("page/<int:page_id>/", views.page_api, name="page_api"),
    path("page/<int:page_id>/posts/", views.page_posts_api, name="page_posts_api"),

    # Post detail + its reviews
    path("post/<int:post_id>/", views.post_detail_api, name="post_detail_api"),

    # Feed (with ?offset= & ?category=)
    path("feed/", views.feed, name="feed"),

    # Create post
    path("review/add/",  views.create_post, name="create_post"),

    # Add review
    path("add-review/", views.add_review, name="add_review"),

    # Get reviews of a post (pagination supported)
    path("post/<int:post_id>/reviews/", views.get_post_reviews, name="get_post_reviews"),
]


