import os
import requests

USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://127.0.0.1:8000/api")


def get_user(user_id):
    pass


def get_user_id_by_username(username):
    try:
        r = requests.get(f"{USER_SERVICE_URL}/lookup/", params={"username": username})
        return r.json().get("id") if r.status_code == 200 else None
    except requests.RequestException:
        return None
