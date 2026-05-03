from django.apps import AppConfig
import atexit


class DeliveryConfig(AppConfig):
    name = "delivery"

    def ready(self):
        import delivery.signals  # noqa
        import delivery.consul_registry as cr  # noqa
        service_id = cr.register_service()
        atexit.register(lambda: cr.deregister_service(service_id))
