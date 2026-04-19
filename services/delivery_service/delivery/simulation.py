"""
delivery/simulation.py

Delivery simulation engine.
Progresses a Delivery through realistic stages with randomized
timing and optional status messages. Can be run:

  - Directly via the management command:
      python manage.py simulate_delivery <delivery_id>

  - Programmatically (e.g. in a background thread):
      from delivery.simulation import simulate_delivery
      import threading
      t = threading.Thread(target=simulate_delivery, args=(delivery,), daemon=True)
      t.start()
"""

import random
import time
import logging
from datetime import timedelta
from django.utils import timezone
from . import payment_webhook as pw
from .models import Delivery

# obserever or logger for simulation(delivery) progress and status messages
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Simulation stages
# Each stage: (status_value, label, min_seconds, max_seconds, messages)
# ---------------------------------------------------------------------------

STAGES = [
    (
        Delivery.DeliveryStatus.PENDING,
        "Order Received",
        3, 8,
        [
            "Order has been received and is being prepared.",
            "Warehouse confirmed your order.",
            "Packaging started.",
        ],
    ),
    (
        Delivery.DeliveryStatus.ACCEPTED,
        "Accepted & Dispatched",
        5, 12,
        [
            "Parcel handed to driver.",
            "Driver picked up your package.",
            "Dispatch confirmed.",
        ],
    ),
    (
        Delivery.DeliveryStatus.IN_TRANSIT,
        "In Transit",
        8, 18,
        [
            "Parcel is on the way.",
            "Driver is en route.",
            "Package left sorting center.",
            "Vehicle moving toward destination.",
            "Estimated 30 min away.",
        ],
    ),
    (
        Delivery.DeliveryStatus.DELIVERED,
        "Delivered",
        2, 5,
        [
            "Package successfully delivered.",
            "Delivery confirmed. Enjoy!",
        ],
    ),
    (
        Delivery.DeliveryStatus.CANCELLED,
        "Cancelled",
        1, 3,
        [
            "Delivery cancelled.",
            "Order has been cancelled.",
        ],
    )
]

# Occasionally inject a realistic hiccup between stages
HICCUP_MESSAGES = [
    "Slight delay due to traffic.",
    "Driver is taking an alternate route.",
    "Brief stop at a checkpoint.",
    "Package re-scanned at relay point.",
]


def simulate_delivery(delivery: Delivery, step_min: int = 60, step_max: int = 120) -> None:
    """
    Advance a delivery through all simulation stages with randomized waits.

    Args:
        delivery:  The Delivery instance to simulate.
        step_min:  Minimum seconds to wait between stage transitions.
        step_max:  Maximum seconds to wait between stage transitions.
    """

    # Log the start of the simulation
    logger.info(f"[SIM] Starting simulation for Delivery #{delivery.pk}")

    for status, label, min_s, max_s, messages in STAGES:

        # Pick a random message for this stage
        message = random.choice(messages)

        # Update delivery in DB
        delivery.delivery_status = status
        delivery.updated_at = timezone.now()

        # Move estimated delivery time forward a bit on each step
        if delivery.estimated_delivery_time < timezone.now():
            delivery.estimated_delivery_time = timezone.now(
            ) + timedelta(minutes=random.randint(5, 30))

        delivery.save(
            update_fields=["delivery_status", "updated_at", "estimated_delivery_time"])
        if status != Delivery.DeliveryStatus.DELIVERED and status != Delivery.DeliveryStatus.CANCELLED:
            # Notify payment service on each status change
            pw.notify_payment(delivery)
        logger.info(f"Delivery #{delivery.pk} → {label}: {message}")

        # Occasionally add a hiccup message (30% chance)
        if random.random() < 0.3 and status not in (Delivery.DeliveryStatus.PENDING, Delivery.DeliveryStatus.DELIVERED):
            hiccup = random.choice(HICCUP_MESSAGES)
            logger.info(f"Delivery #{delivery.pk}, {hiccup}")

        # Stop after delivered
        if status == Delivery.DeliveryStatus.DELIVERED or status == Delivery.DeliveryStatus.CANCELLED:
            logger.info(f"Delivery #{delivery.pk}, simulation complete.")
            # Notify payment service on final status
            pw.notify_payment(delivery)
            break

        # Wait before next stage
        wait = random.randint(step_min, step_max)
        logger.info(f"Delivery #{delivery.pk} waiting {
                    wait}s before next stage...")
        time.sleep(wait)
