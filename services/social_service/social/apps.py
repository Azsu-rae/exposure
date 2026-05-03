from django.apps import AppConfig
import atexit


class SocialConfig(AppConfig):
    name = 'social'

    def ready(self):
        import social.consul_registry as cr  # noqa
        service_id = cr.register_service()
        atexit.register(lambda: cr.deregister_service(service_id))
