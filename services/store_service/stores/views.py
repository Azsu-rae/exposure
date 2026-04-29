from stores.serializers import OrderSerializer, OverviewSerializer,OrderCreateSerializer, ProductSerializer, StoreSerializer
from stores.models import Order, User, Product, Store

from rest_framework.views import APIView
from rest_framework.response import Response
import string, random


class OrdersCreateView(APIView):
    # Depending on your setup, you probably want permission classes here (e.g. IsAuthenticated)
    # permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = OrderCreateSerializer(data=request.data)

        if serializer.is_valid():
            # Inject the requesting user
            order = serializer.save(user=request.user)

            # --- Payment Integration Logic ---
            checkout_url = None
            if order.payment_method.upper() == 'CARD':
                # Replace this logic with your real Chargily POST request!
                random_hash = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
                checkout_url = f"https://checkout.chargily.com/test-url-{random_hash}"

            return Response({
                "message": "Order created successfully",
                "order_id": str(order.order_id),
                "status": order.status,
                "checkout_url": checkout_url
            }, status=201)

        return Response(serializer.errors, status=400)

class OverviewView(APIView):
    def get(self, request, format=None):
        user_base = []
        for user in User.objects.filter(is_activated=True, active_mode="SELLER"):
            if hasattr(user, 'seller_profile') and hasattr(user.seller_profile, 'store'):
                user_base.append({
                    "owner": user.username,
                    "stores": [user.seller_profile.store]
                })
        return Response(OverviewSerializer(user_base, many=True).data)


class ProductsView(APIView):
    def get(self, request, format=None):
        products = Product.objects.filter(is_blocked=False) # Only return approved products
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        from stores.serializers import ProductCreateSerializer
        serializer = ProductCreateSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()

            # AI content detection logic stub
            if product.image:
                try:
                    # from ultralytics import YOLO
                    # model = YOLO("best.pt")
                    # result = model(product.image.path)
                    # if detect_violation(result):
                    #     product.is_blocked = True
                    #     product.save()
                    pass
                except Exception as e:
                    print("AI prediction failed:", e)

            # Auto-generate a linked Post to enter the social feed natively
            if not product.is_blocked:
                try:
                    from social.models import Post
                    Post.objects.create(
                        page=product.store,
                        product=product,
                        title=product.name,
                        description=product.description
                    )
                except Exception as e:
                    print("Could not generate Post for feed:", e)

            return Response({
                "message": "Product created successfully",
                "product_id": product.id,
                "is_blocked": product.is_blocked
            }, status=201)
        return Response(serializer.errors, status=400)


class OrdersView(APIView):
    def get(self, request, format=None):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)