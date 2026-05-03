from django.apps import AppConfig
import atexit


class StoresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stores'

    def ready(self):
        import stores.signals  # noqa
        import stores.consul_registry as cr  # noqa
        service_id = cr.register_service()
        atexit.register(lambda: cr.deregister_service(service_id))
