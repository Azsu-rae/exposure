from rest_framework import serializers

from .models import Payment


class PaymentCreateSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    seller_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    method = serializers.ChoiceField(choices=Payment.Method.choices)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'order_id', 'buyer_id', 'seller_id',
            'amount', 'method', 'status',
            'checkout_url', 'release_date', 'created_at',
        ]
        read_only_fields = fields
