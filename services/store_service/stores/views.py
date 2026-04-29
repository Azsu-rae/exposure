from stores.serializers import OrderSerializer, ProductSerializer
from stores.models import Order, OrderItem, Product, Store
from stores.permissions import IsBuyer, IsSeller

from rest_framework.views import APIView
from rest_framework.response import Response


class ProductsView(APIView):

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSeller()]
        return [IsBuyer()]

    def get(self, request):
        products = Product.objects.filter(is_blocked=False)
        return Response(ProductSerializer(products, many=True).data)

    def post(self, request):
        try:
            store = Store.objects.get(id=request.data.get('store_id'), seller=request.user.id)
        except Store.DoesNotExist:
            return Response({"error": "Store not found or does not belong to you."}, status=404)

        serializer = ProductSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        serializer.save(store=store)
        return Response(serializer.data, status=201)


class OrdersView(APIView):

    def get_permissions(self):
        return [IsBuyer()]

    def get(self, request):
        orders = Order.objects.filter(user=request.user.id)
        return Response(OrderSerializer(orders, many=True).data)

    def post(self, request):
        items_data = request.data.get('items', [])
        if not items_data:
            return Response({"error": "No items provided."}, status=400)

        # validate stock before creating anything
        for item in items_data:
            try:
                product = Product.objects.get(id=item['product_id'], is_blocked=False)
            except Product.DoesNotExist:
                return Response({"error": f"Product {item['product_id']} not found."}, status=404)
            if product.stock < item['quantity']:
                return Response({"error": f"Insufficient stock for {product.name}."}, status=400)

        order = Order.objects.create(
            user=request.user.id,
            shipping_address=request.data.get('shipping_address', ''),
            payment_method=request.data.get('payment_method', ''),
        )

        for item in items_data:
            product = Product.objects.get(id=item['product_id'])
            OrderItem.objects.create(order=order, product=product, quantity=item['quantity'])
            product.stock -= item['quantity']
            product.save()

        return Response(OrderSerializer(order).data, status=201)
