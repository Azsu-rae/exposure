from django.apps import AppConfig
import atexit


class PaymentConfig(AppConfig):
    name = 'payment'

    def ready(self):
        import payment.consul_registry as cr  # noqa
        service_id = cr.register_service()
        atexit.register(lambda: cr.deregister_service(service_id))
