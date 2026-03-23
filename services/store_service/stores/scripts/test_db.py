import django

django.setup()

from stores.models import Store

store = Store(
    name="Titanic",
    description="Expensive coffee shop",
    city="Rouiba",
)

stores = Store.objects.all()
print(stores)

rouiba_stores = Store.objects.filter(city="Rouiba")
print(rouiba_stores)
