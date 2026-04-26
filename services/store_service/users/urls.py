from django.urls import path
from . import views

urlpatterns = [
    # auth
    path("register/",       views.register,       name="register"),
    path("login/",          views.login,          name="login"),
    path("logout/",         views.logout,         name="logout"),

    # current user
    path("me/",             views.me,             name="me"),
    path("me/update/",      views.update_profile, name="update-profile"),
    path("me/buyer/",       views.update_buyer_profile, name="update-buyer-profile"),
    path("me/password/",    views.change_password, name="change-password"),

    # mode switch (the toggle button)
    path("switch-mode/",    views.switch_mode,    name="switch-mode"),

    # seller activation (the one-time form)
    path("activate-seller/",       views.activate_seller,        name="activate-seller"),
    path("me/seller/",             views.update_seller_profile,  name="update-seller-profile"),
    path("me/seller/store/",       views.update_store,           name="update-store"),
]