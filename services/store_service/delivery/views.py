# services/views.py

from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import viewsets

from .serialiser import DeliverySerializer, DriverSerializer, DeliveryCompanySerializer, OfficeSerializer
from .models import Delivery, Driver, DeliveryCompany, RetrievalOffice
from .simulation import simulate_delivery

import json
import time
import random
import threading
import logging


class DeliveryViewSet(viewsets.ModelViewSet):

    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['delivery_status', 'order_id', 'company']

    search_fields = ['delivery_arrival_address']
    ordering_fields = ['updated_at', 'estimated_delivery_time']


class DriverViewSet(viewsets.ModelViewSet):

    queryset = Driver.objects.all()
    serializer_class = DriverSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['company']

    search_fields = ['name', 'phone_number']


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = DeliveryCompany.objects.all()
    serializer_class = DeliveryCompanySerializer


class OfficeViewSet(viewsets.ModelViewSet):
    queryset = RetrievalOffice.objects.all()
    serializer_class = OfficeSerializer


logger = logging.getLogger(__name__)


def _delivery_to_dict(delivery):
    return {
        "id": delivery.pk,
        "order_id": delivery.order_id,
        "delivery_status": delivery.delivery_status,
        "delivery_status_display": delivery.get_delivery_status_display(),
        "delivery_arrival_address": delivery.delivery_arrival_address,
        "estimated_delivery_time": delivery.estimated_delivery_time.isoformat(),
        "updated_at": delivery.updated_at.isoformat(),
    }


@csrf_exempt
@require_http_methods(["POST"])
def start_simulation(request, delivery_id):
    delivery = get_object_or_404(Delivery, pk=delivery_id)

    if delivery.delivery_status == Delivery.DeliveryStatus.DELIVERED:
        return JsonResponse({"error": "This delivery is already delivered."}, status=400)

    print("We should be working?")
    body = {}
    if request.body:
        try:
            print(f"parsing {request.body}")
            body = json.loads(request.body)
            print(f"result: {body}")
        except json.JSONDecodeError:
            print("Exception?")
            pass
    else:
        print("The requestion doesn't actually have a body")

    step_min = int(body.get("step_min", 60))
    step_max = int(body.get("step_max", 120))

    delivery.delivery_status = Delivery.DeliveryStatus.PENDING
    delivery.save(update_fields=["delivery_status", "updated_at"])

    thread = threading.Thread(
        target=simulate_delivery,
        args=(delivery, step_min, step_max),
        daemon=True,
    )
    thread.start()

    return JsonResponse({
        "message": f"Simulation started for Delivery #{delivery_id}.",
        "step_interval": f"{step_min}–{step_max} seconds",
        "stream_url": f"/deliveries/{delivery_id}/stream/",
        "poll_url": f"/deliveries/{delivery_id}/status/",
    })


def _sse_event(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


def stream_delivery(request, delivery_id):
    def event_generator():
        last_status = None
        last_updated = None
        timeout_counter = 0
        max_idle_ticks = 150

        while True:
            try:
                delivery = Delivery.objects.get(pk=delivery_id)
            except Delivery.DoesNotExist:
                yield _sse_event({"error": "Delivery not found.", "done": True})
                break

            current_status = delivery.delivery_status
            current_updated = delivery.updated_at.isoformat()

            if current_status != last_status or current_updated != last_updated:
                timeout_counter = 0
                last_status = current_status
                last_updated = current_updated

                payload = _delivery_to_dict(delivery)
                payload["message"] = _status_message(current_status)
                payload["done"] = current_status in (
                    Delivery.DeliveryStatus.DELIVERED,
                    Delivery.DeliveryStatus.CANCELLED,
                )
                yield _sse_event(payload)

                if payload["done"]:
                    break
            else:
                timeout_counter += 1
                if timeout_counter % 15 == 0:
                    yield _sse_event({"heartbeat": True, "status": current_status})
                if timeout_counter >= max_idle_ticks:
                    yield _sse_event({"error": "Stream timed out.", "done": True})
                    break

            time.sleep(2)

    response = StreamingHttpResponse(
        event_generator(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


def _status_message(status: str) -> str:
    messages = {
        Delivery.DeliveryStatus.PENDING:    "Your order has been received.",
        Delivery.DeliveryStatus.ACCEPTED:   "Order accepted and dispatched to driver.",
        Delivery.DeliveryStatus.IN_TRANSIT: random.choice([
            "Your package is on the way.",
            "Driver is en route.",
            "Package is moving toward you.",
        ]),
        Delivery.DeliveryStatus.DELIVERED:  "Package delivered successfully!",
        Delivery.DeliveryStatus.CANCELLED:  "Delivery was cancelled, package is being returned.",
    }
    return messages.get(status, "Status updated.")


@require_http_methods(["GET"])
def delivery_status(request, delivery_id):
    delivery = get_object_or_404(Delivery, pk=delivery_id)
    data = _delivery_to_dict(delivery)
    data["message"] = _status_message(delivery.delivery_status)
    data["is_final"] = delivery.delivery_status in (
        Delivery.DeliveryStatus.DELIVERED,
        Delivery.DeliveryStatus.CANCELLED,
    )
    return JsonResponse(data)


@require_http_methods(["GET"])
def delivery_by_order(request, order_id):
    deliveries = Delivery.objects.filter(order_id=order_id)
    if not deliveries.exists():
        # Lazy Initialization for backwards compatibility and decoupled creation
        try:
            from stores.models import Order
            order = Order.objects.get(order_id=order_id)
            from django.utils import timezone
            from datetime import timedelta
            delivery = Delivery.objects.create(
                order_id=order_id,
                delivery_arrival_address=order.shipping_address,
                estimated_delivery_time=timezone.now() + timedelta(days=2),
                delivery_status=Delivery.DeliveryStatus.PENDING
            )
        except Exception as e:
            # Order not found or other crash
            return JsonResponse({"error": f"No delivery found and lazy-init failed: {str(e)}"}, status=404)
    else:
        delivery = deliveries.first()
        
    data = _delivery_to_dict(delivery)
    data["message"] = _status_message(delivery.delivery_status)
    data["is_final"] = delivery.delivery_status in (
        Delivery.DeliveryStatus.DELIVERED,
        Delivery.DeliveryStatus.CANCELLED,
    )
    return JsonResponse(data)
