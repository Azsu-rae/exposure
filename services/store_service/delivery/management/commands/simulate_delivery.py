"""
delivery/management/commands/simulate_delivery.py

Run a delivery simulation from the terminal:

    python manage.py simulate_delivery <delivery_id>
    python manage.py simulate_delivery <delivery_id> --min 5 --max 12
"""

from django.core.management.base import BaseCommand, CommandError
from delivery import views
from delivery import models as m
from delivery import simulation as sim
import random
import time
from datetime import timedelta
from django.utils import timezone

STAGES = sim.STAGES
HICCUP_MESSAGES = sim.HICCUP_MESSAGES


class Command(BaseCommand):
    help = "Simulate a delivery progressing through all stages in real time."

    def add_arguments(self, parser):
        parser.add_argument("delivery_id", type=int,
                            help="ID of the Delivery to simulate")
        parser.add_argument("--min", type=int, default=60,  dest="step_min",
                            help="Min seconds between stages (default: 60)")
        parser.add_argument("--max", type=int, default=120, dest="step_max",
                            help="Max seconds between stages (default: 120)")

    def handle(self, *args, **options):
        delivery_id = options["delivery_id"]
        step_min = options["step_min"]
        step_max = options["step_max"]

        try:
            delivery = m.Delivery.objects.select_related(
                "driver", "company").get(pk=delivery_id)
        except m.Delivery.DoesNotExist:
            raise CommandError(f"Delivery #{delivery_id} does not exist.")

        self.stdout.write(self.style.NOTICE(
            f"Starting simulation for Delivery #{delivery.pk} "
            f"(Order {delivery.order_id}) — steps every {
                step_min}–{step_max}s\n"
        ))

        for status, label, min_s, max_s, messages in STAGES:
            message = random.choice(messages)

            delivery.delivery_status = status
            delivery.updated_at = timezone.now()

            if delivery.estimated_delivery_time < timezone.now():
                delivery.estimated_delivery_time = (
                    timezone.now() + timedelta(minutes=random.randint(5, 30))
                )
            delivery.save(
                update_fields=["delivery_status", "updated_at", "estimated_delivery_time"])

            self.stdout.write(
                f"  [{timezone.now().strftime('%H:%M:%S')}] " +
                self.style.SUCCESS(f"{label}") + f"  →  {message}"
            )

            if random.random() < 0.3 and status not in (
                    m.Delivery.DeliveryStatus.PENDING, m.Delivery.DeliveryStatus.DELIVERED, m.Delivery.DeliveryStatus.CANCELLED):
                hiccup = random.choice(HICCUP_MESSAGES)

                self.stdout.write(
                    f"  [{timezone.now().strftime('%H:%M:%S')}] " +
                    self.style.WARNING(f"{hiccup}")
                )

            if status == m.Delivery.DeliveryStatus.DELIVERED:
                self.stdout.write(self.style.SUCCESS(
                    "\n Simulation complete!\n"))
                break
            elif status == m.Delivery.DeliveryStatus.CANCELLED:
                self.stdout.write(self.style.ERROR(
                    "\nDelivery cancelled, simulation ended.\n"))
                break

            wait = random.randint(step_min, step_max)
            self.stdout.write(f"Next update in {wait}s...\n")
            time.sleep(wait)
