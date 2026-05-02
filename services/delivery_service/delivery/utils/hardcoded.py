import uuid
from datetime import timedelta

from django.utils import timezone


SAMPLE_DRIVERS = [
    {"name": "John Smith", "phone_number": "+1-555-0101",
        "location": "Downtown", "rating": 4.8},
    {"name": "Jane Doe", "phone_number": "+1-555-0102",
        "location": "Westside", "rating": 4.5},
    {"name": "Mike Johnson", "phone_number": "+1-555-0103",
        "location": "Eastside", "rating": 4.2},
    {"name": "Sarah Williams", "phone_number": "+1-555-0104",
        "location": "Northgate", "rating": 4.9},
    {"name": "Tom Brown", "phone_number": "+1-555-0105",
        "location": "Southport", "rating": 4.6},
]

SAMPLE_COMPANIES = [
    {"name": "FastShip Express", "contact_number": "+1-555-1001",
        "address": "123 Main St, Downtown"},
    {"name": "QuickDrop Logistics", "contact_number": "+1-555-1002",
        "address": "456 Industrial Ave"},
    {"name": "CityCourier Services", "contact_number": "+1-555-1003",
        "address": "789 Commerce Blvd"},
]

# Deterministic UUIDs so the sample data is repeatable across init_db runs.
SAMPLE_DELIVERIES = [
    {"order_id": uuid.UUID(int=1001), "delivery_arrival_address": "321 Oak St, Downtown"},
    {"order_id": uuid.UUID(int=1002), "delivery_arrival_address": "654 Pine Ave, Westside"},
    {"order_id": uuid.UUID(int=1003), "delivery_arrival_address": "987 Maple Dr, Eastside"},
    {"order_id": uuid.UUID(int=1004), "delivery_arrival_address": "147 Cedar Ln, Northgate"},
    {"order_id": uuid.UUID(int=1005), "delivery_arrival_address": "258 Birch Ct, Southport"},
    {"order_id": uuid.UUID(int=1006), "delivery_arrival_address": "369 Elm St, Downtown"},
    {"order_id": uuid.UUID(int=1007), "delivery_arrival_address": "741 Willow Way, Westside"},
]


def get_estimated_delivery_time():
    return timezone.now() + timedelta(hours=2)
