from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'deliveries', views.DeliveryViewSet)
router.register(r'drivers', views.DriverViewSet)
router.register(r'companies', views.CompanyViewSet)
router.register(r'offices', views.OfficeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('deliveries/<int:delivery_id>/start/', views.start_simulation),
    path('deliveries/<int:delivery_id>/stream/', views.stream_delivery),
    path('deliveries/<int:delivery_id>/status/', views.delivery_status),
    path('delivery-by-order/<str:order_id>/', views.delivery_by_order),
]
