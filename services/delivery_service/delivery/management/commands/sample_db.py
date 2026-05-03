from django.core.management.base import BaseCommand

from delivery.models import Delivery, Driver, DeliveryCompany
from delivery.utils.hardcoded import (
    SAMPLE_DRIVERS,
    SAMPLE_COMPANIES,
    SAMPLE_DELIVERIES,
    get_estimated_delivery_time,
)


class Command(BaseCommand):
    help = "Populate the database with sample data for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing sample data before creating new",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.clear_data()

        drivers = self.create_drivers()
        companies = self.create_companies()
        self.create_deliveries(drivers, companies)

        self.stdout.write(self.style.SUCCESS("Sample data created successfully!"))

    def clear_data(self):
        Delivery.objects.all().delete()
        Driver.objects.all().delete()
        DeliveryCompany.objects.all().delete()
        self.stdout.write(self.style.WARNING("Cleared existing data"))

    def create_drivers(self):
        drivers = []
        for data in SAMPLE_DRIVERS:
            driver, created = Driver.objects.get_or_create(
                phone_number=data["phone_number"],
                defaults=data,
            )
            drivers.append(driver)
            msg = "Created" if created else "Found existing"
            self.stdout.write(f"  {msg} driver: {driver.name}")
        return drivers

    def create_companies(self):
        companies = []
        for data in SAMPLE_COMPANIES:
            company, created = DeliveryCompany.objects.get_or_create(
                contact_number=data["contact_number"],
                defaults=data,
            )
            companies.append(company)
            msg = "Created" if created else "Found existing"
            self.stdout.write(f"  {msg} company: {company.name}")
        return companies

    def create_deliveries(self, drivers, companies):
        for i, data in enumerate(SAMPLE_DELIVERIES):
            driver = drivers[i % len(drivers)]
            company = companies[i % len(companies)]
            delivery, created = Delivery.objects.get_or_create(
                order_id=data["order_id"],
                defaults={
                    "driver": driver,
                    "company": company,
                    "delivery_arrival_address": data["delivery_arrival_address"],
                    "estimated_delivery_time": get_estimated_delivery_time(),
                },
            )
            msg = "Created" if created else "Found existing"
            self.stdout.write(f"  {msg} delivery: Order #{delivery.order_id}")