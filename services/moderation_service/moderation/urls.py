from django.urls import path
from .views import moderate_product_image

urlpatterns = [
    path('moderate/', moderate_product_image, name='moderate_image'),
]
