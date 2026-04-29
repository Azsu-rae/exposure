from rest_framework import serializers
from .models import Order, OrderItem,  Product
from .services import get_user, get_store


# ---------------------------
# PRODUCT
# ---------------------------
class ProductSerializer(serializers.ModelSerializer):
    store = serializers.SerializerMethodField()

    def get_store(self, obj):
        store = get_store(obj.store_id)
        return store.get("name") if store else str(obj.store_id)

    class Meta:
        model = Product
        fields = (
            "id",
            "store",
            "name",
            "description",
            "price",
            "stock",
            "image",
            "is_blocked",
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
            "is_blocked"
        )

    def validate_store(self, value):
        store = get_store(value)
        if not store:
            raise serializers.ValidationError("Invalid store")
        return value


# ---------------------------
# STORE
# ---------------------------


# ---------------------------
# ORDER ITEM
# ---------------------------
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    product_price = serializers.SerializerMethodField()

    def get_product_name(self, obj):
        # assuming product exists locally
        return obj.product.name if obj.product else "Unknown"

    def get_product_price(self, obj):
        return obj.product.price if obj.product else 0

    class Meta:
        model = OrderItem
        fields = (
            "quantity",
            "product_name",
            "product_price",
            "subtotal",
        )


class OrderItemCreateSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField()


# ---------------------------
# ORDER CREATE
# ---------------------------
class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ('shipping_address', 'payment_method', 'items')

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        request = self.context.get('request')
        user_id = request.user.id

        # validate user via service
        user = get_user(user_id)
        if not user:
            raise serializers.ValidationError("Invalid user")

        order = Order.objects.create(
            user_id=user_id,
            **validated_data
        )

        for item in items_data:
            try:
                product = Product.objects.get(id=item['product_id'])
            except Product.DoesNotExist:
                raise serializers.ValidationError("Invalid product")

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity']
            )

        return order


# ---------------------------
# ORDER
# ---------------------------
class OrderSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name='total')

    def get_user(self, obj):
        user = get_user(obj.user_id)
        return user.get("username") if user else str(obj.user_id)

    def total(self, obj):
        return sum(item.subtotal for item in obj.items.all())

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


# ---------------------------
# OVERVIEW
# ---------------------------
class OverviewSerializer(serializers.Serializer):
    owner = serializers.CharField()
    stores = serializers.SerializerMethodField()

