import requests

USER_SERVICE = "http://127.0.0.1:8000/api"
STORE_SERVICE = "http://store-service:8000"


def get_user(user_id):
    r = requests.get(f"{USER_SERVICE}/users/{user_id}")
    return r.json() if r.status_code == 200 else None


def get_product(product_id):
    r = requests.get(f"{STORE_SERVICE}/products/{product_id}")
    return r.json() if r.status_code == 200 else None


def get_store(store_id):
    r = requests.get(f"{USER_SERVICE}/stores/{store_id}")
    return r.json() if r.status_code == 200 else None