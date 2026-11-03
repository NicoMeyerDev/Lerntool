"""Hilfsfunktionen zum Lesen von Umgebungsvariablen für die Einstellungen."""

import os

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
