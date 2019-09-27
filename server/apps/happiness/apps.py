from django.apps import AppConfig


class HappinessConfig(AppConfig):
    name = 'apps.happiness'

    def ready(self):
        from . import signals
