# users/serializers.py
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, SellerProfile, DeliveryProfile


class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ["username", "email", "phone", "password", "password2", "role"]

    def validate_role(self, value):
        if value in ("ADMIN", "DELIVERY"):
            raise serializers.ValidationError("You cannot register with this role.")
        return value

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if user.role == User.Role.SELLER:
            SellerProfile.objects.create(
                user=user,
                store_name=f"{user.username}'s store"
            )

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ["id", "username", "email", "phone", "role"]
        read_only_fields = ["id", "role"]


class SellerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SellerProfile
        fields = ["store_name", "chargily_id", "balance", "is_verified"]
        read_only_fields = ["balance", "is_verified"]


class DeliveryProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DeliveryProfile
        fields = ["company_name", "wilaya", "is_active"]
        read_only_fields = ["is_active"]