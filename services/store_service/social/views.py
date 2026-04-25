from django.shortcuts import render, get_object_or_404, redirect
from .models import Page, Post, Review


def page_view(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    posts = page.posts.all()   # ✅ FIX: only page posts

    return render(request, "social/page.html", {
        "page": page,
        "posts": posts
    })


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        Review.objects.create(
            post=post,
            user=request.user if request.user.is_authenticated else None,  # ✅ fix
            stars=request.POST.get("stars"),
            comment=request.POST.get("comment")
        )
        return redirect("post_detail", post_id=post.id)

    return render(request, "social/post_detail.html", {
        "post": post
    })



#
#
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from django.shortcuts import get_object_or_404
# from .models import Page, Post, Review
# from .serializers import PageSerializer, PostSerializer
#
#
# @api_view(["GET"])
# def page_api(request, page_id):
#     page = get_object_or_404(Page, id=page_id)
#     serializer = PageSerializer(page)
#     return Response(serializer.data)
#
#
# @api_view(["GET", "POST"])
# def post_api(request, post_id):
#     post = get_object_or_404(Post, id=post_id)
#
#     if request.method == "POST":
#         Review.objects.create(
#             post=post,
#             user=request.user,
#             stars=request.data.get("stars"),
#             comment=request.data.get("comment")
#         )
#
#     serializer = PostSerializer(post)
#     return Response(serializer.data)