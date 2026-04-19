from django.urls import path
from .views import OrdersView, ProductsView, OverviewView

urlpatterns = [
    path('orders/', OrdersView.as_view(), name='orders'),
    path('products/', ProductsView.as_view(), name='products'),
    path('overview/', OverviewView.as_view(), name='overview'),
]
