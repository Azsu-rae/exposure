import requests
import socket
import uuid
import os

CONSUL_URL = "http://localhost:8500"

SERVICE_NAME = "social"
SERVICE_PORT = int(os.environ.get("PORT", 8000))

def register_service():
    service_id = f"{SERVICE_NAME}-{SERVICE_PORT}"
    hostname = socket.gethostbyname(socket.gethostname())

    payload = {
        "Name": SERVICE_NAME,
        "ID": service_id,
        "Address": hostname,
        "Port": SERVICE_PORT,
        "Check": {
            "HTTP": f"http://{hostname}:{SERVICE_PORT}/api/social/health/",
            "Interval": "10s"
        }
    }

    requests.put(f"{CONSUL_URL}/v1/agent/service/register", json=payload)
    print(f"[Consul] Registered {service_id} on {hostname}:{SERVICE_PORT}")

    return service_id


def deregister_service(service_id):
    requests.put(f"{CONSUL_URL}/v1/agent/service/deregister/{service_id}")
    print(f"[Consul] Deregistered {service_id}")