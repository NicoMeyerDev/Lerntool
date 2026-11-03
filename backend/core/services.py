"""Geschäftslogik der Kern-App."""

import logging

from django.db import DatabaseError, connection

logger = logging.getLogger(__name__)


def datenbank_erreichbar() -> bool:
    """Prüft, ob die Datenbank eine einfache Abfrage beantwortet.

    Returns:
        True, wenn `SELECT 1` erfolgreich war, sonst False.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        logger.exception("Health-Check: Datenbank nicht erreichbar.")
        return False
    return True
