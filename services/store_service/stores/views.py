from stores.serializers import (
    OrderSerializer,
    OverviewSerializer,
    ProductSerializer
)

from stores.models import Order, Product
from stores.services import get_user

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# ---------------------------
# OVERVIEW
# ---------------------------
class OverviewView(APIView):
    def get(self, request, format=None):
        user_id = request.user.id

        user = get_user(user_id)
        owner = user.get("username") if user else "unknown"

        # since Store is NOT in this service anymore
        data = {
            "owner": owner,
            "stores": []  # must come from user-service or gateway
        }

        return Response(data)


# ---------------------------
# PRODUCTS
# ---------------------------
class ProductsView(APIView):
    def get(self, request, format=None):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------
# ORDERS
# ---------------------------
class OrdersView(APIView):
    def get(self, request, format=None):
        user_id = request.user.id

        orders = Order.objects.filter(user_id=user_id)
        serializer = OrderSerializer(orders, many=True)

        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = OrderSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            order = serializer.save()
            return Response(
                OrderSerializer(order).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)