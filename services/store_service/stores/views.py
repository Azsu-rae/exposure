
from stores.serializers import OrderSerializer, OverviewSerializer
from stores.models import Order, User

from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(["GET"])
def order_list(request):
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def user_base(request):
    user_base = [{
        "owner": user.username,
        "stores": user.stores.all()
    } for user in User.objects.all()]
    return Response(OverviewSerializer(user_base, many=True).data)
