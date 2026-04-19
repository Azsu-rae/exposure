from django.db import models

# delivery is the representation of the shipment of the order


class Delivery(models.Model):
    class DeliveryStatus(models.TextChoices):
        PENDING = 'Pending'
        IN_TRANSIT = 'In Transit'
        DELIVERED = 'Delivered'
        CANCELLED = 'Cancelled'
        ACCEPTED = 'Accepted'

    """
    order_id is a refernece to the orders table in the order service, it is not a foreign key to avoid tight
    coupling between services
    """

    order_id = models.IntegerField()
    driver = models.ForeignKey('Driver', on_delete=models.CASCADE)
    company = models.ForeignKey('DeliveryCompany', on_delete=models.CASCADE)
    delivery_arrival_address = models.CharField(max_length=255)
    delivery_status = models.CharField(
        max_length=50,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING
    )
    updated_at = models.DateTimeField(auto_now=True)
    estimated_delivery_time = models.DateTimeField()

    def __str__(self):
        return f"Delivery {self.pk} for Order {self.order_id}"


class Driver(models.Model):
    """
    a driver can be independent or can be associated with a delivery company, if the driver is independent, the
    company field will be null
    """
    company = models.ForeignKey(
        'DeliveryCompany',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    location = models.CharField(max_length=255)

    # rating is a float field that represents the average rating of the driver, it is updated after each delivery is
    # completed and rated by the customer
    rating = models.FloatField()

    def __str__(self):
        return self.name


class DeliveryCompany(models.Model):
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class RetrievalOffice(models.Model):
    """
    retrieval office is a location where the delivery company can store the packages after they are delivered to
    the customers, it is associated with a delivery company
    """
    company = models.ForeignKey('DeliveryCompany', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)

    def __str__(self):
        return self.name
