from django.db import models
import uuid

# Address as a separate model (composition with Store)
class StoreAddress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    wilaya = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.wilaya}"

# Main Store model
class Store(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('SUSPENDED', 'Suspended'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    owner_id = models.UUIDField()  # Reference to User Service
    created_at = models.DateTimeField(auto_now_add=True)

    # Composition: Each Store has one address
    address = models.OneToOneField(StoreAddress, on_delete=models.CASCADE, related_name='store')

    def __str__(self):
        return self.name
