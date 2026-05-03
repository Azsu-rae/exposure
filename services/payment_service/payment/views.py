from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Payment
from .serializers import PaymentCreateSerializer, PaymentSerializer
from .simulator import process_new_payment
from .permissions import IsBuyer, IsDelivery

from django.http import StreamingHttpResponse, JsonResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes


@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    return JsonResponse({'status': 'ok'})


class PaymentViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Payment.objects.all().order_by('-created_at')
        if user.role == 'BUYER':
            return qs.filter(buyer_id=user.id)
        if user.role == 'SELLER':
            return qs.filter(seller_id=user.id)
        return qs

    def get_permissions(self):
        if self.action == 'create_payment':
            return [IsBuyer()]
        if self.action == 'mark_collected':
            return [IsDelivery()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'], url_path='create')
    def create_payment(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if Payment.objects.filter(order_id=data['order_id']).exists():
            return Response({'error': 'Payment already exists for this order.'}, status=400)

        payment = Payment.objects.create(
            order_id=data['order_id'],
            seller_id=data['seller_id'],
            buyer_id=request.user.id,
            amount=data['amount'],
            method=data['method'],
        )
        payment = process_new_payment(payment)
        return Response(PaymentSerializer(payment).data, status=201)

    @action(detail=True, methods=['post'], url_path='mark-collected')
    def mark_collected(self, request, pk=None):
        """Cash-on-delivery confirmation by the courier. Flips PENDING→HELD."""
        payment = self.get_object()
        if payment.method != Payment.Method.CASH:
            return Response({'error': 'Only cash payments can be marked collected.'}, status=400)
        if payment.status != Payment.Status.PENDING:
            return Response({'error': f'Payment is in {payment.status}, cannot mark collected.'}, status=400)
        payment.status = Payment.Status.HELD
        payment.save(update_fields=['status'])
        return Response(PaymentSerializer(payment).data)
