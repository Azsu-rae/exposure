import os
import requests

import store_service.settings as settings

USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://127.0.0.1:8000/api")
INTERNAL_SECRET = settings.env("INTERNAL_API_SECRET", default="")


def get_user(user_id):
    pass


def get_user_id_by_username(username):
    try:
        r = requests.get(
            f"{USER_SERVICE_URL}/internal/lookup/",
            params={"username": username},
            headers={"X-Internal-Secret": INTERNAL_SECRET},
        )
        return r.json().get("id") if r.status_code == 200 else None
    except requests.RequestException:
        return None
