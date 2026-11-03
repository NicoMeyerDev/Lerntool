"""Tests für die Anmeldung per Token und den Zugriffsschutz der API."""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from tests.fabrik import Inhalte

pytestmark = pytest.mark.django_db


def test_login_liefert_token(nutzer: User) -> None:
    """Mit richtigen Zugangsdaten gibt es ein Token, das dem Nutzer gehört."""
    antwort = APIClient().post(
        reverse("login"), {"username": "lernender", "password": "geheim-123"}, format="json"
    )

    assert antwort.status_code == 200
    assert Token.objects.get(user=nutzer).key == antwort.json()["token"]


def test_login_mit_falschem_passwort_wird_abgelehnt(nutzer: User) -> None:
    """Falsche Zugangsdaten führen zu 400 und keinem Token."""
    antwort = APIClient().post(
        reverse("login"), {"username": "lernender", "password": "falsch"}, format="json"
    )

    assert antwort.status_code == 400
    assert "token" not in antwort.json()


def test_login_wird_nach_zehn_versuchen_gebremst(nutzer: User) -> None:
    """Nach 10 Versuchen pro Minute antwortet der Login mit 429."""
    client = APIClient()
    daten = {"username": "lernender", "password": "falsch"}
    for _ in range(10):
        assert client.post(reverse("login"), daten, format="json").status_code == 400

    assert client.post(reverse("login"), daten, format="json").status_code == 429


def test_ich_liefert_angemeldeten_nutzer(client_angemeldet: APIClient, nutzer: User) -> None:
    """`/api/auth/ich/` nennt ID und Benutzernamen."""
    antwort = client_angemeldet.get(reverse("ich"))

    assert antwort.status_code == 200
    assert antwort.json() == {"id": nutzer.pk, "benutzername": "lernender"}


def test_logout_macht_token_ungueltig(client_angemeldet: APIClient) -> None:
    """Nach dem Logout wird das alte Token abgelehnt."""
    assert client_angemeldet.post(reverse("logout")).status_code == 204

    assert client_angemeldet.get(reverse("ich")).status_code == 401


def test_ungueltiges_token_wird_abgelehnt() -> None:
    """Ein erfundenes Token führt zu 401."""
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Token erfunden")

    assert client.get(reverse("themen")).status_code == 401


@pytest.mark.parametrize(
    ("methode", "name", "kwargs"),
    [
        ("get", "ich", {}),
        ("post", "logout", {}),
        ("get", "themen", {}),
        ("get", "thema", {"slug": "php-laravel"}),
        ("get", "lektion", {"pk": 1}),
        ("get", "quiz", {"pk": 1}),
        ("post", "quiz-abgabe", {"pk": 1}),
        ("post", "abschnitt-gelesen", {"pk": 1}),
        ("get", "fortschritt", {}),
    ],
)
def test_alle_endpunkte_ausser_health_und_login_brauchen_anmeldung(
    inhalte: Inhalte, methode: str, name: str, kwargs: dict[str, str | int]
) -> None:
    """Ohne Token antworten alle geschützten Endpunkte mit 401."""
    client = APIClient()
    antwort = getattr(client, methode)(reverse(name, kwargs=kwargs))

    assert antwort.status_code == 401


@pytest.mark.parametrize("daten", [{}, {"username": "lernender"}, {"password": "geheim-123"}])
def test_login_ohne_vollstaendige_zugangsdaten_wird_abgelehnt(
    nutzer: User, daten: dict[str, str]
) -> None:
    """Fehlt Benutzername oder Passwort, gibt es 400 und kein Token."""
    antwort = APIClient().post(reverse("login"), daten, format="json")

    assert antwort.status_code == 400
    assert not Token.objects.exists()
