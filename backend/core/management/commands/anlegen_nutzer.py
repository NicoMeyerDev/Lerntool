"""Verwaltungsbefehl: legt den einzigen Nutzer der App aus Umgebungsvariablen an."""

import logging
import os
from typing import Any

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Legt beim Deployment den eigenen Zugang an, falls es noch keinen Nutzer gibt.

    Gedacht für Hosting ohne Shell-Zugang (z. B. Render, kostenloser Tarif).
    Liest `LERNTOOL_BENUTZER` und `LERNTOOL_PASSWORT`. Existiert schon ein Nutzer,
    passiert nichts. Der Befehl ist daher gefahrlos bei jedem Start wiederholbar
    und überschreibt nie ein bestehendes Passwort.
    """

    help = "Legt den Nutzer aus LERNTOOL_BENUTZER/LERNTOOL_PASSWORT an, falls keiner existiert."

    def handle(self, *args: Any, **options: Any) -> None:
        """Führt den Befehl aus.

        Args:
            *args: Nicht verwendet.
            **options: Nicht verwendet.

        Raises:
            CommandError: Wenn kein Nutzer existiert und die Umgebungsvariablen fehlen
                oder das Passwort die Passwortregeln der App verletzt.
        """
        if User.objects.exists():
            self.stdout.write("Nutzer vorhanden, nichts zu tun.")
            return
        benutzer = os.environ.get("LERNTOOL_BENUTZER", "").strip()
        passwort = os.environ.get("LERNTOOL_PASSWORT", "")
        if not benutzer or not passwort:
            logger.error("LERNTOOL_BENUTZER oder LERNTOOL_PASSWORT fehlt.")
            raise CommandError("LERNTOOL_BENUTZER und LERNTOOL_PASSWORT müssen gesetzt sein.")
        try:
            validate_password(passwort, user=User(username=benutzer))
        except ValidationError as fehler:
            logger.error("Passwort für den ersten Nutzer abgelehnt: %s", "; ".join(fehler.messages))
            raise CommandError(
                "LERNTOOL_PASSWORT ist zu schwach: " + " ".join(fehler.messages)
            ) from fehler
        User.objects.create_user(username=benutzer, password=passwort)
        self.stdout.write(f"Nutzer {benutzer} angelegt.")
