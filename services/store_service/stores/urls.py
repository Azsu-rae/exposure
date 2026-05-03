from django.urls import path, include
from rest_framework import routers
from .views import StoreViewSet, ProductViewSet, OrderViewSet, health

router = routers.DefaultRouter()
router.register(r'stores', StoreViewSet, basename='store')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('store/health/', health)
]
