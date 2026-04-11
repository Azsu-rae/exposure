from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.order_list),
    path('user_base/', views.user_base),
]
