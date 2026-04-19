from django.contrib import admin
from .models import Delivery, Driver, DeliveryCompany, RetrievalOffice

# Register your models here.
admin.site.register(Delivery)
admin.site.register(Driver)
admin.site.register(DeliveryCompany)
admin.site.register(RetrievalOffice)
