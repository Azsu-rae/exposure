from django.urls import path
from . import views

urlpatterns = [
    # path("api/page/<int:page_id>/", views.page_api),
    # path("api/post/<int:post_id>/", views.post_api),

    path("page/<int:page_id>/", views.page_view, name="page"),
    path("post/<int:post_id>/", views.post_detail, name="post_detail"),
    # path('index/<int:x>',views.index)
]

