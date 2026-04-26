from rest_framework.permissions import BasePermission


class IsActivatedSeller(BasePermission):
    """User completed the seller form — regardless of active_mode."""
    message = "Complete seller registration first."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_activated


class IsInSellerMode(BasePermission):
    """User is activated AND currently in SELLER mode."""
    message = "Switch to seller mode first."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_activated
            and request.user.active_mode == "SELLER"
        )


class IsInBuyerMode(BasePermission):
    """Any authenticated user in BUYER mode (all users can buy)."""
    message = "Switch to buyer mode first."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.active_mode == "BUYER"
        )