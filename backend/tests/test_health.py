"""Tests für den Health-Check-Endpunkt `/api/health/`."""

import pytest
from django.db import DatabaseError, connection
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from core import services


@pytest.mark.django_db
def test_health_meldet_ok_bei_erreichbarer_datenbank() -> None:
    """Bei laufender Datenbank antwortet der Endpunkt mit 200 und Status ok."""
    antwort = APIClient().get(reverse("health"))

    assert antwort.status_code == 200
    assert antwort.json() == {"status": "ok", "datenbank": "ok"}


def test_health_meldet_503_bei_datenbankfehler(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ist die Datenbank nicht erreichbar, antwortet der Endpunkt mit 503."""
    monkeypatch.setattr("core.views.datenbank_erreichbar", lambda: False)

    antwort = APIClient().get(reverse("health"))

    assert antwort.status_code == 503
    assert antwort.json() == {"status": "fehler", "datenbank": "nicht erreichbar"}


def test_datenbank_erreichbar_faengt_datenbankfehler_ab(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Der Service liefert False statt einer Ausnahme, wenn die Abfrage scheitert."""

    def wirft_fehler() -> None:
        """Simuliert eine fehlschlagende Datenbankverbindung."""
        raise DatabaseError("Verbindung abgelehnt")

    monkeypatch.setattr(connection, "cursor", wirft_fehler)

    assert services.datenbank_erreichbar() is False


def test_health_braucht_keine_anmeldung(monkeypatch: pytest.MonkeyPatch) -> None:
    """Der Endpunkt bleibt ohne Anmeldung erreichbar, auch wenn global Login Pflicht ist."""
    monkeypatch.setattr("core.views.datenbank_erreichbar", lambda: True)
    pflicht_login = {"DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"]}

    with override_settings(REST_FRAMEWORK=pflicht_login):
        antwort = APIClient().get(reverse("health"))

    assert antwort.status_code == 200
