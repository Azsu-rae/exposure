# users/views.py

from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from django.contrib.auth import authenticate

from .models import SellerProfile, User
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    SellerProfileSerializer,
)


def get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access":  str(refresh.access_token),
    }


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):

    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    user = authenticate(**serializer.validated_data)
    if not user:
        return Response({"error": "Invalid username or password."}, status=401)

    tokens = get_tokens(user)
    return Response({
        "user":   UserSerializer(user).data,
        "tokens": tokens,
    })


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):

    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    user = serializer.save()
    tokens = get_tokens(user)
    return Response({
        "message": "Account created successfully.",
        "user":    UserSerializer(user).data,
        "tokens":  tokens,
    }, status=201)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    if not user.check_password(request.data.get("old_password")):
        return Response({"error": "Old password is incorrect."}, status=400)
    user.set_password(request.data.get("new_password"))
    user.save()
    return Response({"message": "Password changed successfully."})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        token = RefreshToken(request.data.get("refresh"))
        token.blacklist()
        return Response({"message": "Logged out successfully."})
    except Exception:
        return Response({"error": "Invalid or expired token."}, status=400)


@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_token(request):
    try:
        token = RefreshToken(request.data.get("refresh"))
        return Response({"access": str(token.access_token)})
    except Exception:
        return Response({"error": "Invalid or expired refresh token."}, status=401)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_profile(request):
    user = request.user
    data = UserSerializer(user).data
    if user.is_seller:
        try:
            data["seller_profile"] = SellerProfileSerializer(
                user.seller_profile).data
        except SellerProfile.DoesNotExist:
            data["seller_profile"] = None
    return Response(data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_profile(request):

    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    serializer.save()
    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_seller_profile(request):
    if not request.user.is_seller:
        return Response({"error": "Only sellers can access this."}, status=403)
    serializer = SellerProfileSerializer(
        request.user.seller_profile,
        data=request.data,
        partial=True
    )
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    serializer.save()
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_account(request):
    request.user.delete()
    return Response({"message": "Account deleted."}, status=204)
