from django.apps import AppConfig


class JournalConfig(AppConfig):
    name = "src.journal"

    def ready(self):
        import src.journal.signals
