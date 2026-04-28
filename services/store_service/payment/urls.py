
from django.urls import path
from . import views

urlpatterns = [
    path("payments/",                                    views.payment_list),
    path("payments/create/",                             views.create_payment),
    path("payments/webhook/",                            views.chargily_webhook),
    path("payments/<int:payment_id>/confirm-delivery/",  views.confirm_delivery),
    path('payments/pending-payouts/', views.pending_payouts),
    path('payments/<int:payment_id>/mark-paid-out/', views.mark_paid_out),
]

# path('<int:payment_id>/release/', release_payment),
    # path('<int:payment_id>/refund/', request_refund),