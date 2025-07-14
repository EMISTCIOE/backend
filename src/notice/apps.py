from django.apps import AppConfig


class NoticeConfig(AppConfig):
    name = 'src.notice'

    def ready(self):
        import src.notice.signals
