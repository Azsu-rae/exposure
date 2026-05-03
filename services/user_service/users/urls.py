# users/urls.py

from django.urls import path
from . import views

urlpatterns = [

    path("users/health/",        views.health),

    path("users/register/",        views.register),
    path("users/change-password/", views.change_password),

    path("users/login/",           views.login),
    path("users/logout/",          views.logout),

    path("users/refresh/",         views.refresh_token),

    path("profile/",              views.my_profile),
    path("profile/update/",       views.update_profile),
    path("profile/seller/",       views.update_seller_profile),
    path("profile/delete/",       views.delete_account),

    path("lookup/",               views.lookup_user),
    path("internal/lookup/",      views.internal_lookup_user),
]
