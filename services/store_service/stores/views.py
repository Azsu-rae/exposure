from stores.serializers import ProductSerializer, OrderSerializer, OrderItemSerializer
from stores.models import Product, Order, OrderItem
from users.models import Store
from users.serializers import StoreSerializer

from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(["GET"])
def product_list(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def product_details(request, pk):
    product = Product.objects.filter(id=pk)[0]
    serializer = ProductSerializer(product)
    return Response(serializer.data)


@api_view(["GET"])
def order_list(request):
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)
