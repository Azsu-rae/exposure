import json

from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from .models import Payment
from .services import create_checkout, client
from .serializers import PaymentCreateSerializer, PaymentSerializer
from ..users.permissions import IsBuyer, IsDelivery

# 📊 LIST PAYMENTS
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def payment_list(request):
    payments = Payment.objects.all()
    serializer = PaymentSerializer(payments, many=True)
    return Response(serializer.data)


# 💳 CREATE PAYMENT

@api_view(["POST"])
@permission_classes([IsBuyer])
def create_payment(request):
    serializer = PaymentCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    validated = serializer.validated_data
    order_id = validated["order_id"]
    amount   = validated["amount"]
    method   = validated["method"]

    # ... rest of your logic unchanged
    if not order_id or not amount:
        return Response({"error": "order_id and amount are required"}, status=400)

    if method not in ("CASH", "CARD"):
        return Response({"error": "method must be CASH or CARD"}, status=400)

    # 💵 CASH — no Chargily, confirmed on delivery
    if method == "CASH":
        payment = Payment.objects.create(
            order_id=order_id,
            amount=amount,
            method="CASH",
            status="PENDING",
        )
        return Response({
            "message": "Cash payment registered. Confirm on delivery.",
            "payment_id": payment.id,
            "status": payment.status,
        })

    # 💳 CARD — redirect to Chargily checkout
    payment = Payment.objects.create(
        order_id=order_id,
        amount=amount,
        method="CARD",
        status="PENDING",
    )
    payment = create_checkout(payment)
    return Response({
        "checkout_url": payment.checkout_url,
        "status": payment.status,
    })


# 🚚 CONFIRM DELIVERY (triggers escrow release or refund)
@api_view(["POST"])
@permission_classes([IsDelivery])
def confirm_delivery(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=404)

    delivered = request.data.get("delivered")
    returned = request.data.get("returned")

    # CASH payments are PENDING until delivery — allow release from PENDING too
    if payment.status not in ("HELD", "PENDING"):
        return Response(
            {"error": f"Cannot confirm delivery for a payment with status: {payment.status}"},
            status=400
        )

    # Cash payments that are PENDING should only be released, not refunded here
    # (refund only makes sense after money was actually collected)
    if payment.method == "CASH" and payment.status == "PENDING" and returned:
        return Response(
            {"error": "Cash payment was never collected — nothing to refund"},
            status=400
        )

    if delivered and not returned:
        payment.status = "RELEASED"
        payment.release_date = timezone.now()
        payment.save()
        return Response({"message": "Money released to seller"})

    if returned:
        payment.status = "REFUNDED"
        payment.save()
        return Response({"message": "Refunded to buyer"})

    return Response({"message": "Waiting for confirmation"})


# 🔔 CHARGILY WEBHOOK
@csrf_exempt
def chargily_webhook(request):
    signature = request.headers.get("signature")
    payload = request.body.decode("utf-8")

    if not signature:
        return HttpResponse(status=400)

    if not client.validate_signature(signature, payload):
        return HttpResponse(status=403)

    event = json.loads(payload)
    checkout_id = event["data"]["id"]
    event_type = event["type"]

    payment = Payment.objects.filter(entity_id=checkout_id).first()
    if not payment:
        return HttpResponse(status=404)

    # Prevent processing the same webhook twice
    if payment.status != "PENDING":
        return HttpResponse(status=200)

    if event_type == "checkout.paid":
        payment.status = "HELD"  # escrow begins here
        payment.save()

    elif event_type == "checkout.failed":
        payment.status = "FAILED"
        payment.save()

    return HttpResponse(status=200)