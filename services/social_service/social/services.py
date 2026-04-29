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


# --- NEW BULK FETCHERS ---

def get_users_bulk(user_ids):
    """
    Ideally, your USER_SERVICE should have an endpoint like POST /users/bulk 
    that accepts a list of IDs. I am simulating it here.
    """
    if not user_ids: return {}
    unique_ids = set(user_ids)

    # BEST CASE: 
    # r = requests.post(f"{USER_SERVICE}/users/bulk", json={"ids": list(unique_ids)})
    # return r.json() # Should return a dict like { "1": {user_data}, "2": {user_data} }

    # FALLBACK (Until you build the bulk endpoint on the other service):
    result = {}
    for uid in unique_ids:
        user = get_user(uid)
        if user:
            result[uid] = user
    return result


def get_products_bulk(product_ids):
    if not product_ids: return {}
    unique_ids = set(product_ids)

    # BEST CASE: 
    # r = requests.post(f"{STORE_SERVICE}/products/bulk", json={"ids": list(unique_ids)})
    # return r.json()

    # FALLBACK:
    result = {}
    for pid in unique_ids:
        prod = get_product(pid)
        if prod:
            result[pid] = prod
    return result


def get_stores_bulk(store_ids):
    if not store_ids: return {}
    unique_ids = set(store_ids)

    # Ideally, call a bulk endpoint on your User/Store service:
    # r = requests.post(f"{USER_SERVICE}/stores/bulk/", json={"ids": list(unique_ids)})

    # Fallback loop (until you have a bulk endpoint):
    result = {}
    for sid in unique_ids:
        store = get_store(sid)
        if store:
            result[sid] = {
                "name": store.get("name"),
                "logo": store.get("logo")  # This will be the image URL
            }
    return result