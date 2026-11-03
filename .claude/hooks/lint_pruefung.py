"""PostToolUse-Hook: prüft geänderte Dateien mit dem passenden Linter.

Fehler gehen mit Exit-Code 2 an Claude zurück. Fehlt ein Werkzeug oder
das Projekt ist noch leer, wird still übersprungen.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def linter_befehl(datei: Path, projekt: Path) -> tuple[list[str], Path] | None:
    """Wählt Linter-Befehl und Arbeitsordner passend zur Dateiendung.

    Args:
        datei: Die geänderte Datei.
        projekt: Der Projekt-Hauptordner.
    """
    if datei.suffix == ".py" and shutil.which("ruff"):
        return ["ruff", "check", str(datei)], projekt
    frontend = projekt / "frontend"
    npx = shutil.which("npx")
    if datei.suffix in {".ts", ".tsx"} and npx and (frontend / "node_modules").exists():
        return [npx, "eslint", str(datei)], frontend
    return None


def main() -> None:
    """Liest den Hook-Aufruf von stdin und führt den Linter aus."""
    daten = json.load(sys.stdin)
    pfad = daten.get("tool_input", {}).get("file_path", "")
    if not pfad:
        return
    projekt = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
    auswahl = linter_befehl(Path(pfad), projekt)
    if auswahl is None:
        return
    befehl, ordner = auswahl
    ergebnis = subprocess.run(befehl, cwd=ordner, capture_output=True, text=True, timeout=120)
    if ergebnis.returncode != 0:
        print(ergebnis.stdout + ergebnis.stderr, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
