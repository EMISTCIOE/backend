from django.apps import AppConfig


class HomeConfig(AppConfig):
    name = 'src.home'

    def ready(self):
        import src.home.signals
