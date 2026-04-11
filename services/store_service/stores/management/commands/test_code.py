from django.core.management.base import BaseCommand

from stores.models import Product, Store, User, Order
from stores.serializers import StoreSerializer, UserBaseSerializer

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import serializers

from datetime import datetime

import io


class CommentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    content = serializers.CharField(max_length=200)
    created = serializers.DateTimeField()


class Comment:
    def __init__(self, email, content, created=None):
        self.email = email
        self.content = content
        self.created = created or datetime.now()


class Command(BaseCommand):
    help = "testing some code"

    def handle(self, *args, **kwargs):
        self.aggregator()

    def aggregator(self):
        users = [{
            "owner": user.username,
            "stores": user.stores.all()
        } for user in User.objects.all()]
        user_base = UserBaseSerializer(users, many=True)
        print(f"{user_base.data=}")

    def model_seriazlizing(self):
        stores = Store.objects.all()
        print(f"{StoreSerializer(stores, many=True)=}")

    def serializing(self):
        comment = Comment(email='leila@example.com', content='foo bar')
        serializer = CommentSerializer(comment)
        print(f"{type(serializer.data)=}")
        print(f"{serializer.data=}")
        print(f"{serializer.data["email"]=}")
        if True:
            exit()
        json = JSONRenderer().render(serializer.data)
        print(f"{type(json)=}")
        print(f"{json=}")
        stream = io.BytesIO(json)
        data = JSONParser().parse(stream)
        print(f"{type(data)=}")
        print(f"{data=}")
        serializer = CommentSerializer(data=data)
        print(f"{serializer.is_valid()=}")
        print(f"{serializer.validated_data=}")

    def reverse_relations(self):
        print(f"\n{User.objects.get(username="abdellaoui_mohamed").store_set.all()=}")
        print(f"\n{Order.objects.filter(user=1)[0].items.all()=}")
        print(f"\n{Order.objects.filter(user=1)[0].products.all()=}")
        print(f"\n{Product.objects.get(name="Smart Watch").items.all()[0]=}")
        print(f"\n{Product.objects.get(name="Smart Watch").order_set.all()=}")

    def iterate(self):
        stores = Store.objects.prefetch_related("product_set")
        for s in stores:
            self.stdout.write(f"\n{s.name}:\n\n")
            products = s.product_set.all()
            for p in products:
                self.stdout.write(f"- {p.name}")

    def create_superuser(self):
        return User.objects.create_superuser(
            username="Ilyas",
            email="aitameurmedilyas@gmail.com",
            password="ilyaspass"
        )
