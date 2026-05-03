from django.urls import include, path
from rest_framework import routers

from delivery.views import (
    DeliveryViewSet, DriverViewSet, CompanyViewSet, OfficeViewSet,
    StartSimulationView, StreamDeliveryView, DeliveryStatusView,
)

from delivery import views

router = routers.DefaultRouter()
router.register(r'deliveries', DeliveryViewSet)
router.register(r'drivers', DriverViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'offices', OfficeViewSet)

urlpatterns = [
    path('api/delivery/health/', views.health),

    path('api/', include(router.urls)),

    path('api/deliveries/<int:delivery_id>/simulate/start/', StartSimulationView.as_view(), name='start_simulation'),
    path('api/deliveries/<int:delivery_id>/stream/',         StreamDeliveryView.as_view(),  name='stream_delivery'),
    path('api/deliveries/<int:delivery_id>/status/',         DeliveryStatusView.as_view(),  name='delivery_status'),
]
