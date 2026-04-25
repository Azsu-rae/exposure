# users/permissions.py
from rest_framework.permissions import BasePermission


class IsSeller(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "SELLER"


class IsBuyer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "BUYER"


class IsDelivery(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "DELIVERY"


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "ADMIN"