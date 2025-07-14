from django.apps import AppConfig


class DepartmentConfig(AppConfig):
    name = 'src.department'

    def ready(self):
        import src.department.signals
