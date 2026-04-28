from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import BuyerProfile
from .permissions import IsActivatedSeller, IsInSellerMode
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    UpdateProfileSerializer, UpdateBuyerProfileSerializer,
    SellerActivationSerializer, UpdateSellerProfileSerializer,
    UpdateStoreSerializer,
)


# ── helpers ───────────────────────────────────────────────────────────────────

def get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


# ── Auth ──────────────────────────────────────────────────────────────────────

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    s = RegisterSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    user = s.save()
    return Response(
        {"user": UserSerializer(user).data, "tokens": get_tokens(user)},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    print("LOGIN REQUEST DATA:", request.data)
    s = LoginSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    user = s.validated_data["user"]
    return Response({"user": UserSerializer(user).data, "tokens": get_tokens(user)})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        RefreshToken(request.data["refresh"]).blacklist()
    except Exception:
        pass  # already invalid — still return 200
    return Response({"detail": "Logged out."})


# ── Current user ──────────────────────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update base user fields (name, phone, wilaya, address, avatar)."""
    s = UpdateProfileSerializer(request.user, data=request.data, partial=True)
    s.is_valid(raise_exception=True)
    s.save()
    return Response(UserSerializer(request.user).data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_buyer_profile(request):
    """Update buyer-specific fields (default address, wilaya)."""
    profile, _ = BuyerProfile.objects.get_or_create(user=request.user)
    s = UpdateBuyerProfileSerializer(profile, data=request.data, partial=True)
    s.is_valid(raise_exception=True)
    s.save()
    return Response(UserSerializer(request.user).data)


# ── Mode switching ────────────────────────────────────────────────────────────

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def switch_mode(request):
    """
    Toggle BUYER ↔ SELLER.
    If not activated → 403 so Flutter can redirect to activation form.
    """
    try:
        request.user.switch_mode()
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

    return Response({
        "active_mode": request.user.active_mode,
        "user": UserSerializer(request.user).data,
    })


# ── Seller activation ─────────────────────────────────────────────────────────

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def activate_seller(request):
    """
    The one-time form that creates SellerProfile + Store atomically.
    After this, switch_mode works freely.
    """
    s = SellerActivationSerializer(data=request.data, context={"request": request})
    s.is_valid(raise_exception=True)
    user = s.save()
    return Response(
        {"user": UserSerializer(user).data},
        status=status.HTTP_201_CREATED,
    )


# ── Seller profile & store updates (post-activation) ─────────────────────────

@api_view(["PATCH"])
@permission_classes([IsActivatedSeller])
def update_seller_profile(request):
    s = UpdateSellerProfileSerializer(
        request.user.seller_profile,
        data=request.data,
        partial=True,
    )
    s.is_valid(raise_exception=True)
    s.save()
    return Response(UserSerializer(request.user).data)


@api_view(["PATCH"])
@permission_classes([IsActivatedSeller])
def update_store(request):
    s = UpdateStoreSerializer(
        request.user.seller_profile.store,
        data=request.data,
        partial=True,
    )
    s.is_valid(raise_exception=True)
    s.save()
    return Response(UserSerializer(request.user).data)


# ── Password ──────────────────────────────────────────────────────────────────

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    user         = request.user
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")

    if not old_password or not new_password:
        return Response({"detail": "Both fields required."}, status=400)

    if not user.check_password(old_password):
        return Response({"detail": "Wrong current password."}, status=400)

    if len(new_password) < 8:
        return Response({"detail": "Password must be at least 8 characters."}, status=400)

    user.set_password(new_password)
    user.save()
    return Response({"detail": "Password updated."})