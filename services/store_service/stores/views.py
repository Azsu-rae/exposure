from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404

from stores.serializers import OrderSerializer, ProductSerializer, StoreSerializer
from stores.models import Order, OrderItem, Product, Store
from stores.permissions import IsBuyer, IsSeller

from django.http import StreamingHttpResponse, JsonResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes


@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    return JsonResponse({'status': 'ok'})


class StoreViewSet(viewsets.ModelViewSet):
    serializer_class = StoreSerializer

    def get_queryset(self):
        return Store.objects.all()

    def get_permissions(self):
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return [IsAuthenticated()]
        return [IsSeller()]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user.id)


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(is_blocked=False)

    def get_permissions(self):
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return [IsBuyer()]
        return [IsSeller()]

    def perform_create(self, serializer):
        store = get_object_or_404(Store, id=self.request.data.get('store_id'), seller=self.request.user.id)
        serializer.save(store=store)


class OrderViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsBuyer]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user.id)

    def create(self, request, *args, **kwargs):
        items_data = request.data.get('items', [])
        if not items_data:
            return Response({"error": "No items provided."}, status=400)

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
