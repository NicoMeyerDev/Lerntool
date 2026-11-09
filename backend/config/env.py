"""Hilfsfunktionen zum Lesen von Umgebungsvariablen für die Einstellungen."""

import os
from datetime import date

from django.core.exceptions import ImproperlyConfigured


def env_bool(name: str, default: bool = False) -> bool:
    """Liest eine Umgebungsvariable als Wahrheitswert.

    Args:
        name: Name der Umgebungsvariable.
        default: Rückgabewert, wenn die Variable nicht gesetzt ist.

    Returns:
        True bei "1", "true", "yes" oder "on" (ohne Groß-/Kleinschreibung),
        sonst False.
    """
    wert = os.environ.get(name)
    if wert is None:
        return default
    return wert.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    """Liest eine kommagetrennte Umgebungsvariable als Liste.

    Args:
        name: Name der Umgebungsvariable.
        default: Kommagetrennter Standardwert, wenn die Variable fehlt.

    Returns:
        Liste der nicht leeren, von Leerzeichen befreiten Einträge.
    """
    roh = os.environ.get(name, default)
    return [eintrag.strip() for eintrag in roh.split(",") if eintrag.strip()]


def env_required(name: str) -> str:
    """Liest eine Pflicht-Umgebungsvariable.

    Args:
        name: Name der Umgebungsvariable.

    Returns:
        Den gesetzten, nicht leeren Wert.

    Raises:
        ImproperlyConfigured: Wenn die Variable fehlt oder leer ist.
    """
    wert = os.environ.get(name, "").strip()
    if not wert:
        raise ImproperlyConfigured(f"Umgebungsvariable {name} fehlt. Siehe backend/.env.example.")
    return wert


def env_date(name: str, default: str) -> date:
    """Liest eine Umgebungsvariable als Datum im Format JJJJ-MM-TT.

    Args:
        name: Name der Umgebungsvariable.
        default: Standardwert im Format JJJJ-MM-TT, wenn die Variable fehlt oder leer ist.

    Returns:
        Das Datum.

    Raises:
        ImproperlyConfigured: Wenn der Wert kein gültiges Datum im Format JJJJ-MM-TT ist.
    """
    roh = os.environ.get(name, "").strip() or default
    try:
        return date.fromisoformat(roh)
    except ValueError as fehler:
        raise ImproperlyConfigured(
            f"Umgebungsvariable {name} muss ein Datum im Format JJJJ-MM-TT sein, ist aber {roh!r}."
        ) from fehler
