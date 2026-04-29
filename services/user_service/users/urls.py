# users/urls.py

from django.urls import path
from . import views

urlpatterns = [

    path("auth/register/",        views.register),
    path("auth/change-password/", views.change_password),

    path("auth/login/",           views.login),
    path("auth/logout/",          views.logout),

    path("auth/refresh/",         views.refresh_token),

    path("profile/",              views.my_profile),
    path("profile/update/",       views.update_profile),
    path("profile/seller/",       views.update_seller_profile),
    path("profile/delete/",       views.delete_account),

    path("lookup/",               views.lookup_user),
]
