"""Befehl `python manage.py import_inhalte`: Lerninhalte aus YAML-Dateien importieren."""

from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import IntegrityError

from lernen.inhalte_import import InhaltsFehler, importiere_inhalte


class Command(BaseCommand):
    """Prüft die Inhaltsdateien und importiert sie in die Datenbank."""

    help = "Importiert Lerninhalte aus YAML-Dateien (Standard: backend/inhalte). Löscht nichts."

    def add_arguments(self, parser: CommandParser) -> None:
        """Definiert das optionale Verzeichnis.

        Args:
            parser: Der Argument-Parser des Befehls.
        """
        parser.add_argument(
            "verzeichnis",
            nargs="?",
            default=str(Path(settings.BASE_DIR) / "inhalte"),
            help="Ordner mit den Themen-Ordnern",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Führt den Import aus und gibt einen kurzen Bericht aus.

        Args:
            *args: Nicht genutzt.
            **options: Enthält `verzeichnis`.

        Raises:
            CommandError: Wenn die Dateien Fehler enthalten (dann wird nichts gespeichert).
        """
        try:
            bericht = importiere_inhalte(Path(options["verzeichnis"]))
        except IntegrityError as ex:
            raise CommandError(
                f"Import abgebrochen, nichts gespeichert: Datenbank lehnt die Inhalte ab ({ex})"
            ) from ex
        except InhaltsFehler as ex:
            raise CommandError(
                "\n".join(["Import abgebrochen, nichts gespeichert:", *ex.meldungen])
            ) from ex
        self.stdout.write(
            self.style.SUCCESS(
                f"{bericht.phasen} Phasen, {bericht.lektionen} Lektionen, "
                f"{bericht.abschnitte} Abschnitte, "
                f"{bericht.fragen} Fragen, {bericht.projekte} Projekte importiert."
            )
        )
        for warnung in bericht.warnungen:
            self.stdout.write(self.style.WARNING(f"Warnung: {warnung}"))
