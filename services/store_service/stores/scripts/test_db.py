import django

django.setup()

from stores.models import Store

store = Store(
    name="Titanic",
    description="Expensive coffee shop",
    city="Rouiba",
)

print(store)
print("hello??")
