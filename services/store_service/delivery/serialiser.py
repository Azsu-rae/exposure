from rest_framework import serializers
from .models import Delivery, Driver, DeliveryCompany, RetrievalOffice


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = '__all__'


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = '__all__'


class OfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetrievalOffice
        fields = '__all__'


class DeliveryCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryCompany
        fields = '__all__'

