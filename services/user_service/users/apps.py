from django.apps import AppConfig
import atexit

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        from .consul_register import register_service, deregister_service

        service_id = register_service()

        # deregister on shutdown
        atexit.register(lambda: deregister_service(service_id))
