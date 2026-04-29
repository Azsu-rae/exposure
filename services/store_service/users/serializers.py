from django.db import transaction
from rest_framework import serializers
from .models import User, BuyerProfile, SellerProfile, Store


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model  = User
        fields = ["id", "username", "email", "password", "phone"]

    def create(self, validated_data):
        return User.objects.create_user(
            username = validated_data["username"],
            email    = validated_data["email"],
            password = validated_data["password"],
            phone    = validated_data.get("phone"),
        )
        # BuyerProfile created automatically via signal


class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        from django.contrib.auth import authenticate
        # allow login by email — requires EMAIL_BACKEND or custom backend
        user = authenticate(username=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        data["user"] = user
        return data


# ── User read ─────────────────────────────────────────────────────────────────

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Store
        fields = [
            "id", "name", "description", "logo",
            "wilaya", "city", "ccp",
            "is_active", "rating", "created_at",
        ]


class SellerProfileSerializer(serializers.ModelSerializer):
    store = StoreSerializer(read_only=True)

    class Meta:
        model  = SellerProfile
        fields = [
            "bio", "is_verified", "balance",
            "rating", "created_at", "store",
        ]


class BuyerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = BuyerProfile
        fields = ["default_wilaya", "default_address", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    buyer_profile  = BuyerProfileSerializer(read_only=True)
    seller_profile = SellerProfileSerializer(read_only=True)  # null if not activated

    class Meta:
        model  = User
        fields = [
            "id", "username", "email", "phone",
            "profile_picture", "wilaya", "address",
            "is_activated", "active_mode",'is_staff',
            "buyer_profile", "seller_profile",
            "created_at",
        ]


# ── Profile updates ───────────────────────────────────────────────────────────

class UpdateProfileSerializer(serializers.ModelSerializer):
    """Buyer updates their own basic info."""
    class Meta:
        model  = User
        fields = ["username", "phone", "profile_picture", "wilaya", "address"]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UpdateBuyerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = BuyerProfile
        fields = ["default_wilaya", "default_address"]


# ── Seller activation (the big form) ─────────────────────────────────────────

class SellerActivationSerializer(serializers.Serializer):
    # personal — updates the User fields
    phone   = serializers.CharField(max_length=20)
    wilaya  = serializers.CharField(max_length=100)
    address = serializers.CharField()
    bio     = serializers.CharField(required=False, allow_blank=True, default="")
    id_document = serializers.ImageField(required=False, allow_null=True)

    # store — creates Store under SellerProfile
    store_name        = serializers.CharField(max_length=100)
    store_description = serializers.CharField(required=False, allow_blank=True, default="")
    store_wilaya      = serializers.CharField(max_length=100)
    store_city        = serializers.CharField(max_length=100)
    ccp               = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    logo              = serializers.ImageField(required=False, allow_null=True)

    def validate(self, data):
        user = self.context["request"].user
        if user.is_activated:
            raise serializers.ValidationError("Already activated as a seller.")
        return data

    @transaction.atomic
    def save(self):
        user = self.context["request"].user
        d    = self.validated_data

        # update user personal fields
        user.phone   = d["phone"]
        user.wilaya  = d["wilaya"]
        user.address = d["address"]
        user.activate_seller()           # is_activated=True, active_mode=SELLER, save()

        seller = SellerProfile.objects.create(
            user=user, 
            bio=d["bio"],
            id_document=d.get("id_document")
        )

        Store.objects.create(
            seller      = seller,
            name        = d["store_name"],
            description = d["store_description"],
            wilaya      = d["store_wilaya"],
            city        = d["store_city"],
            ccp         = d.get("ccp", ""),
            logo        = d.get("logo")
        )
        return user


# ── Seller profile update (after activation) ─────────────────────────────────

class UpdateSellerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SellerProfile
        fields = ["bio", "id_document"]


class UpdateStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Store
        fields = ["name", "description", "logo", "wilaya", "city",
                  "ccp", "is_active"]