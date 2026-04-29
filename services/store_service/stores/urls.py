from django.urls import path
from .views import OrdersView, ProductsView

urlpatterns = [
    path('orders/', OrdersView.as_view(), name='orders'),
    path('products/', ProductsView.as_view(), name='products'),
]
