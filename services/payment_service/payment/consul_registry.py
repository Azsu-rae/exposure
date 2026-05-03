import requests
import socket
import os

import payment_service.settings as settings

# Ideally, point this to your local Consul agent (e.g., http://localhost:8500 or http://consul:8500)
# Using ngrok for the agent URL can cause latency or health check issues.
CONSUL_URL = settings.env("CONSUL_URL", default="http://localhost:8500")

SERVICE_NAME = "payment"
SERVICE_PORT = int(settings.env("PORT", default="8000"))


def register_service():
    service_id = f"{SERVICE_NAME}-{SERVICE_PORT}"

    # Better approach for Docker: Use an ENV var for the IP, fallback to socket
    hostname = os.environ.get(
        "HOST_IP", socket.gethostbyname(socket.gethostname()))

    payload = {
        "Name": SERVICE_NAME,
        "ID": service_id,
        "Address": hostname,
        "Port": SERVICE_PORT,
        "Tags": [
            "traefik.enable=true",
            "traefik.http.routers.payment.rule="
            "PathPrefix(`/api/payments`) || PathPrefix(`/api/payment`)",
            "traefik.http.routers.payment.entrypoints=web",
        ],
        "Check": {
            "HTTP": f"http://{hostname}:{SERVICE_PORT}/api/{SERVICE_NAME}/health/",
            "Interval": "10s"
        }
    }

    try:
        requests.put(f"{CONSUL_URL}/v1/agent/service/register", json=payload)
        print(f"[Consul] Registered {service_id} on {hostname}:{SERVICE_PORT}")
    except Exception as e:
        print(f"[Consul] Failed to register service: {e}")

    return service_id


def deregister_service(service_id):
    requests.put(f"{CONSUL_URL}/v1/agent/service/deregister/{service_id}")
    print(f"[Consul] Deregistered {service_id}")
