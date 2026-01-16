from django.apps import AppConfig


class HueyLogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_huey_log"

    def ready(self):
        from . import signals  # noqa: F401
