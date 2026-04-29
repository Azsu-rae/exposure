
from django.urls import path
from . import views

urlpatterns = [
    path("payments/",                                    views.payment_list),
    path("create/",                             views.create_payment),
    path("webhook/",                            views.chargily_webhook),
    path("<int:payment_id>/confirm-delivery/",  views.confirm_delivery),
    path("by-order/<str:order_id>/",            views.payment_by_order),
    path("pending-payouts/", views.pending_payouts, name="pending-payouts"),
    path("<int:payment_id>/mark-paid-out/", views.mark_paid_out, name="mark-paid-out"),
]

# path('<int:payment_id>/release/', release_payment),
    # path('<int:payment_id>/refund/', request_refund),