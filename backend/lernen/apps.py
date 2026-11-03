"""App-Konfiguration der Lern-App."""

from django.apps import AppConfig


class LernenConfig(AppConfig):
    """Registriert die App für Lerninhalte und Fortschritt bei Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "lernen"
    verbose_name = "Lernen"
