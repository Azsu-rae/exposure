from django.apps import AppConfig


class StoresConfig(AppConfig):
    name = "stores"

    def ready(self):
        import stores.signals  # noqa
