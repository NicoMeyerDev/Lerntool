"""Tests für das Dashboard (B5): XP, Level, Statistik, Abzeichen und Meilensteine.

Modelle werden als Modul `m` importiert, damit pytest das Modell `Test` nicht sammelt.
"""

from typing import Any

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient

from lernen import models as m
from lernen.dashboard import XP_PRO_LEVEL, berechne_level
from tests.fabrik import Inhalte, baue_frage

pytestmark = pytest.mark.django_db


def lade(client: APIClient) -> Any:
    """Ruft das Dashboard ab.

    Args:
        client: Angemeldeter API-Client.

    Returns:
        Den JSON-Inhalt der Antwort.
    """
    antwort = client.get(reverse("dashboard"))
    assert antwort.status_code == 200
    return antwort.json()


def abzeichen(daten: Any, schluessel: str) -> bool:
    """Liest, ob ein Abzeichen erreicht ist.

    Args:
        daten: Antwort des Dashboards.
        schluessel: Schlüssel des Abzeichens.

    Returns:
        Ob das Abzeichen erreicht ist.
    """
    return bool(next(a["erreicht"] for a in daten["abzeichen"] if a["schluessel"] == schluessel))


@pytest.mark.parametrize(
    ("xp", "level", "im_level"),
    [(0, 1, 0), (99, 1, 99), (XP_PRO_LEVEL, 2, 0), (250, 3, 50)],
)
def test_level_aus_xp(xp: int, level: int, im_level: int) -> None:
    """Alle 100 XP steigt das Level um eins."""
    assert berechne_level(xp) == (level, im_level)


def test_ohne_anmeldung_401(inhalte: Inhalte) -> None:
    """Das Dashboard verlangt eine Anmeldung."""
    assert APIClient().get(reverse("dashboard")).status_code == 401


def test_leerer_stand(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Ohne Fortschritt: 0 XP, Level 1, keine Treffer-Quote, keine Abzeichen."""
    daten = lade(client_angemeldet)

    assert (daten["xp"], daten["level"], daten["xp_im_level"]) == (0, 1, 0)
    statistik = daten["statistik"]
    assert statistik["abschnitte_gelesen"] == 0
    assert statistik["abschnitte_gesamt"] == 1
    assert statistik["trefferquote_prozent"] is None
    assert not any(a["erreicht"] for a in daten["abzeichen"])
    assert daten["themen"] == [
        {"slug": "php-laravel", "titel": "PHP/Laravel", "erledigt": 0, "gesamt": 4}
    ]


def test_xp_aus_allen_quellen(client_angemeldet: APIClient, inhalte: Inhalte, nutzer: User) -> None:
    """Abschnitt 10, Quiz 5 je Punkt, Test 10 je Punkt, Projekt 50 XP."""
    m.Fortschritt.objects.create(nutzer=nutzer, abschnitt=inhalte.abschnitt)
    m.Fortschritt.objects.create(nutzer=nutzer, quiz=inhalte.quiz, punkte=2, max_punkte=3)
    m.Fortschritt.objects.create(nutzer=nutzer, test=inhalte.test, punkte=3, max_punkte=4)
    m.Fortschritt.objects.create(
        nutzer=nutzer, projektaufgabe=inhalte.projekt, punkte=2, max_punkte=2
    )

    daten = lade(client_angemeldet)

    assert daten["xp"] == 10 + 2 * 5 + 3 * 10 + 50
    assert (daten["level"], daten["xp_im_level"]) == (2, 0)
    assert daten["statistik"]["trefferquote_prozent"] == round(5 / 7 * 100)
    assert daten["themen"][0]["erledigt"] == 4


def test_abzeichen_und_meilensteine(
    client_angemeldet: APIClient, inhalte: Inhalte, nutzer: User
) -> None:
    """Abzeichen werden nach Fortschritt vergeben, Meilensteine zeigen das nächste Ziel."""
    m.Fortschritt.objects.create(nutzer=nutzer, abschnitt=inhalte.abschnitt)
    m.Fortschritt.objects.create(nutzer=nutzer, quiz=inhalte.quiz, punkte=3, max_punkte=3)

    daten = lade(client_angemeldet)

    assert abzeichen(daten, "erster-schritt")
    assert abzeichen(daten, "volle-punktzahl")
    assert not abzeichen(daten, "testlauf")
    assert not abzeichen(daten, "projekt-geschafft")
    abschnitte = next(x for x in daten["meilensteine"] if x["schluessel"] == "abschnitte")
    assert (abschnitte["aktuell"], abschnitte["ziel"], abschnitte["erreicht"]) == (1, 10, False)


def test_nicht_volle_punktzahl_gibt_kein_volltreffer(
    client_angemeldet: APIClient, inhalte: Inhalte, nutzer: User
) -> None:
    """Ein Quiz mit Fehlern vergibt das Volltreffer-Abzeichen nicht."""
    m.Fortschritt.objects.create(nutzer=nutzer, quiz=inhalte.quiz, punkte=2, max_punkte=3)

    assert not abzeichen(lade(client_angemeldet), "volle-punktzahl")


def test_level_3_abzeichen(client_angemeldet: APIClient, inhalte: Inhalte, nutzer: User) -> None:
    """Ab 200 XP gibt es das Level-3-Abzeichen."""
    m.Fortschritt.objects.create(nutzer=nutzer, test=inhalte.test, punkte=20, max_punkte=20)

    daten = lade(client_angemeldet)

    assert daten["level"] == 3
    assert abzeichen(daten, "level-3")


def test_letzte_stufe_eines_meilensteins(
    client_angemeldet: APIClient, inhalte: Inhalte, nutzer: User
) -> None:
    """Ist die höchste Stufe erreicht, bleibt sie das Ziel und gilt als erreicht."""
    m.Fortschritt.objects.create(nutzer=nutzer, test=inhalte.test, punkte=100, max_punkte=100)

    xp = next(x for x in lade(client_angemeldet)["meilensteine"] if x["schluessel"] == "xp")

    assert (xp["aktuell"], xp["ziel"], xp["erreicht"]) == (1000, 1000, True)


def test_fortschritt_anderer_nutzer_zaehlt_nicht(
    client_angemeldet: APIClient, inhalte: Inhalte
) -> None:
    """Das Dashboard zeigt nur den eigenen Fortschritt."""
    fremder = User.objects.create_user(username="fremd", password="geheim-123")
    m.Fortschritt.objects.create(nutzer=fremder, abschnitt=inhalte.abschnitt)

    assert lade(client_angemeldet)["xp"] == 0


def test_mehrere_themen_getrennt(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Der Fortschritt wird je Thema gezählt; ein leeres Thema hat 0 von 0."""
    m.Thema.objects.create(titel="Englisch", slug="englisch", reihenfolge=2)

    themen = lade(client_angemeldet)["themen"]

    assert [(t["slug"], t["gesamt"]) for t in themen] == [("php-laravel", 4), ("englisch", 0)]


def test_wenige_abfragen(
    client_angemeldet: APIClient, inhalte: Inhalte, django_assert_max_num_queries: Any
) -> None:
    """Die Berechnung braucht eine feste, kleine Zahl Abfragen."""
    baue_frage(inhalte.quiz, 1)
    for nummer in range(2, 5):
        m.Thema.objects.create(titel=f"Thema {nummer}", slug=f"thema-{nummer}", reihenfolge=nummer)

    with django_assert_max_num_queries(15):
        client_angemeldet.get(reverse("dashboard"))
