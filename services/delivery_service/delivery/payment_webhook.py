# services/payment_client.py
import requests
import logging
from django.conf import settings
from .models import Delivery

logger = logging.getLogger(__name__)


def notify_payment(delivery: Delivery) -> bool:
    payment_url = getattr(settings, 'PAYMENT_URL', None)

    if not payment_url:
        logger.warning("[PAYMENT] PAYMENT_URL not set or invalid.")
        return False

    payload = {
        "order_id": delivery.order_id,
        "delivery_success": delivery.delivery_status == Delivery.DeliveryStatus.DELIVERED,
        "delivery_status": delivery.delivery_status,
    }

    try:
        response = requests.post(payment_url, json=payload, timeout=5)
        response.raise_for_status()
        logger.info(f"[PAYMENT] Notified payment service for order #{
                    delivery.order_id}")

        return True
    except requests.Timeout:
        logger.error(f"[PAYMENT] Timeout for order #{delivery.order_id}")
    except requests.RequestException as e:
        logger.error(f"[PAYMENT] Error for order #{delivery.order_id}: {e}")

    return False
