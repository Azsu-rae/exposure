from django.apps import AppConfig
import atexit


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        import users.signals  # noqa: F401
        import users.consul_registry as cr  # noqa
        service_id = cr.register_service()
        atexit.register(lambda: cr.deregister_service(service_id))
