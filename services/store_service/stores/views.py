
from stores.serializers import OrderSerializer, OverviewSerializer, ProductSerializer, StoreSerializer
from stores.models import Order, User, Product, Store

from rest_framework.views import APIView
from rest_framework.response import Response


class OverviewView(APIView):
    def get(self, request, format=None):
        user_base = [{
            "owner": user.username,
            "stores": user.stores.all()
        } for user in User.objects.all()]
        return Response(OverviewSerializer(user_base, many=True).data)


class ProductsView(APIView):
    def get(self, request, format=None):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        print(request.body)
        return Response({})


class OrdersView(APIView):
    def get(self, request, format=None):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
