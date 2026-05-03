from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter

from .serialiser import DeliverySerializer, DriverSerializer, DeliveryCompanySerializer, OfficeSerializer
from .models import Delivery, Driver, DeliveryCompany, RetrievalOffice
from .permissions import IsAdmin, IsDelivery
from .simulation import simulate_delivery

import json
import time
import random
import threading
import logging


from django.http import StreamingHttpResponse, JsonResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes


@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    return JsonResponse({'status': 'ok'})


logger = logging.getLogger(__name__)


class DeliveryViewSet(viewsets.ModelViewSet):

    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['delivery_status', 'order_id', 'company']

    search_fields = ['delivery_arrival_address']
    ordering_fields = ['updated_at', 'estimated_delivery_time']

    def get_permissions(self):
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return [IsAuthenticated()]
        return [IsDelivery()]


class DriverViewSet(viewsets.ModelViewSet):

    queryset = Driver.objects.all()
    serializer_class = DriverSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['company']

    search_fields = ['name', 'phone_number']

    def get_permissions(self):
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return [IsAuthenticated()]
        return [IsAdmin()]


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = DeliveryCompany.objects.all()
    serializer_class = DeliveryCompanySerializer

    def get_permissions(self):
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return [IsAuthenticated()]
        return [IsAdmin()]


class OfficeViewSet(viewsets.ModelViewSet):
    queryset = RetrievalOffice.objects.all()
    serializer_class = OfficeSerializer

    def get_permissions(self):
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return [IsAuthenticated()]
        return [IsAdmin()]


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


def _sse_event(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


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


class StartSimulationView(APIView):
    permission_classes = [IsDelivery]

    def post(self, request, delivery_id):
        delivery = get_object_or_404(Delivery, pk=delivery_id)

        if delivery.delivery_status == Delivery.DeliveryStatus.DELIVERED:
            return Response({"error": "This delivery is already delivered."}, status=400)

        step_min = int(request.data.get("step_min", 60))
        step_max = int(request.data.get("step_max", 120))

        delivery.delivery_status = Delivery.DeliveryStatus.PENDING
        delivery.save(update_fields=["delivery_status", "updated_at"])

        threading.Thread(
            target=simulate_delivery,
            args=(delivery, step_min, step_max),
            daemon=True,
        ).start()

        return Response({
            "message": f"Simulation started for Delivery #{delivery_id}.",
            "step_interval": f"{step_min}–{step_max} seconds",
            "stream_url": f"/api/deliveries/{delivery_id}/stream/",
            "poll_url": f"/api/deliveries/{delivery_id}/status/",
        })


class StreamDeliveryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, delivery_id):
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

        response = StreamingHttpResponse(event_generator(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response


class DeliveryStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, delivery_id):
        delivery = get_object_or_404(Delivery, pk=delivery_id)
        data = _delivery_to_dict(delivery)
        data["message"] = _status_message(delivery.delivery_status)
        data["is_final"] = delivery.delivery_status in (
            Delivery.DeliveryStatus.DELIVERED,
            Delivery.DeliveryStatus.CANCELLED,
        )
        return Response(data)
