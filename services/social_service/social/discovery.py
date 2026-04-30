import requests

CONSUL_URL = "http://localhost:8500"

def get_user_service_url():
    """
    Query Consul to find a healthy instance of the 'user' service.
    Returns the base URL (e.g., 'http://192.168.100.8:8005') of the first healthy instance,
    or None if no healthy instance is available.
    """
    try:
        # ?passing=true ensures we only get instances whose health checks are passing
        response = requests.get(f"{CONSUL_URL}/v1/health/service/user?passing=true")
        response.raise_for_status()
        instances = response.json()
        
        if instances:
            # We'll just take the first healthy instance found
            service_info = instances[0].get("Service", {})
            address = service_info.get("Address")
            port = service_info.get("Port")
            
            if address and port:
                return f"http://{address}:{port}"
                
    except Exception as e:
        print(f"[Discovery] Error fetching 'user' service from Consul: {e}")
        
    return None
