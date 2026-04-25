from rest_framework import serializers
from .models import Payment


# Used for POST /payments/create/
# Controls what the client is ALLOWED to send
class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["order_id", "amount", "method"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_method(self, value):
        if value not in ("CASH", "CARD"):
            raise serializers.ValidationError("Method must be CASH or CARD.")
        return value


# Used for GET /payments/
# Controls what the client is ALLOWED to see
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "order_id",
            "amount",
            "method",
            "status",
            "checkout_url",  # needed so frontend can redirect user to Chargily
            "release_date",
            "created_at",
        ]
        # these fields are set by the server, never by the client
        read_only_fields = [
            "id",
            "status",
            "checkout_url",
            "release_date",
            "created_at",
        ]