from rest_framework import serializers
from .models import Order, OrderItem, Store, Product


class StoreSerializer(serializers.ModelSerializer):
    seller = serializers.IntegerField(read_only=True)

    class Meta:
        model = Store
        fields = [
            "id", "seller", "name", "description",
            "wilaya", "city", "created_at",
            "is_active", "rating", "ccp"
        ]


class ProductSerializer(serializers.ModelSerializer):

    store = StoreSerializer(read_only=True)
    is_blocked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = (
            "store",
            "name",
            "description",
            "price",
            "stock",
            # "image",
            "is_blocked",
            "category",
        )


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        source='product.price'
    )

    class Meta:
        model = OrderItem
        fields = (
            "quantity",
            "product_name",
            "product_price",
            "subtotal",
        )


class OrderSerializer(serializers.ModelSerializer):

    user = serializers.IntegerField(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    total_price = serializers.SerializerMethodField(method_name='total')
#    delivery_status = serializers.SerializerMethodField(method_name='get_delivery_status')

    def total(self, obj):
        items = obj.items.all()
        return sum(item.subtotal for item in items)

#    def get_delivery_status(self, obj):
#        try:
#            from delivery.models import Delivery
#            delivery = Delivery.objects.filter(order_id=str(obj.order_id)).first()
#            if delivery:
#                return delivery.delivery_status
#            return "Pending"
#        except Exception:
#            return "Pending"

    class Meta:
        model = Order
        fields = (
            "order_id",

            "user",
            "shipping_address",
            "payment_method",
            "created_at",
            "status",
            # "delivery_status",

            "items",
            "total_price",
        )
