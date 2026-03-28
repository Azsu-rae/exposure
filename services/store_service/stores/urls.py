from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="stores-index"),
    path("health/", views.health_check, name="stores-health"),
]
