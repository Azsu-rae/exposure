from rest_framework import serializers
from .models import Order, OrderItem, Store


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
    # by default, 'user' would be a 'PrimaryKeyRelatedField'
    # good alternatives are: 'HyperLinkRelatedField', 'SlugRelatedField'
    user = serializers.StringRelatedField(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name='total')

    def total(self, obj):
        items = obj.items.all()
        return sum(item.subtotal for item in items)

    class Meta:
        model = Order
        fields = (
            "user",
            "order_id",
            "created_at",
            "status",
            "items",
            "total_price",
        )


class StoreSerializer(serializers.ModelSerializer):
    products_nb = serializers.SerializerMethodField(method_name='product_count')

    def product_count(self, obj):
        return len(obj.products.all())

    class Meta:
        model = Store
        fields = (
            "name",
            "products_nb",
        )


class OverviewSerializer(serializers.Serializer):
    """
    owner: "myself"
    stores: [
        {
            name:
            products_nb:
        }
    ]
    """
    owner = serializers.CharField()
    stores = StoreSerializer(many=True, read_only=True)
