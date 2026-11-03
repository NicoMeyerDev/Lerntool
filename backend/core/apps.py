"""App-Konfiguration der Kern-App."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Registriert die Kern-App bei Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
