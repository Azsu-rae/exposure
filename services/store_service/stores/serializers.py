from rest_framework import serializers
from .models import Order, OrderItem, Store, Product


class ProductSerializer(serializers.ModelSerializer):
    store = serializers.CharField(source='store.name')
    store_id = serializers.IntegerField(source='store.id', read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "store",
            "store_id",
            "name",
            "description",
            "price",
            "stock",
            "image",
            "is_blocked",
            "category",
        )

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "store",
            "name",
            "description",
            "price",
            "image",
            "is_blocked",
            "category"
        )


class StoreSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='name')
    products_nb = serializers.SerializerMethodField(method_name='product_count')
    products = ProductSerializer(many=True)

    def product_count(self, obj):
        return len(obj.products.all())

    class Meta:
        model = Store
        fields = (
            "id",
            "store_name",
            "description",
            "logo",
            "rating",
            "products_nb",
            "products",
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


class OrderItemCreateSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product'
    )
    quantity = serializers.IntegerField()


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ('shipping_address', 'payment_method', 'items')

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        # Create the Order base first
        order = Order.objects.create(**validated_data)

        # Create the OrderItem relations
        for item_data in items_data:
            OrderItem.objects.create(
                order=order,
                product=item_data['product'],
                quantity=item_data['quantity']
            )

        return order


class OrderSerializer(serializers.ModelSerializer):
    # by default, 'user' would be a 'PrimaryKeyRelatedField'
    # good alternatives are: 'HyperLinkRelatedField', 'SlugRelatedField'
    user = serializers.StringRelatedField(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name='total')
    delivery_status = serializers.SerializerMethodField()

    def total(self, obj):
        items = obj.items.all()
        return sum(item.subtotal for item in items)
        
    def get_delivery_status(self, obj):
        try:
            from delivery.models import Delivery
            delivery = Delivery.objects.filter(order_id=str(obj.order_id)).first()
            if delivery:
                return delivery.delivery_status
            return "Pending"
        except Exception:
            return "Pending"

    class Meta:
        model = Order
        fields = (
            "user",
            "order_id",
            "created_at",
            "status",
            "delivery_status",
            "items",
            "total_price",
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