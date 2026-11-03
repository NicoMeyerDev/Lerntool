"""Tests für den Wochen- und Tagesplan (B6).

Modelle werden als Modul `m` importiert, damit pytest das Modell `Test` nicht sammelt.
"""

from datetime import date, datetime, timedelta
from typing import Any

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from lernen import models as m
from lernen.wochenplan import montag_der_woche
from tests.fabrik import Inhalte

pytestmark = pytest.mark.django_db

#: Ein Mittwoch (2026-11-04) als Bezugsdatum.
MITTWOCH = date(2026, 11, 4)


def lade(client: APIClient, datum: str | None = None) -> Any:
    """Ruft den Wochenplan ab.

    Args:
        client: Angemeldeter API-Client.
        datum: Optionaler Parameter `datum`.

    Returns:
        Den JSON-Inhalt der Antwort.
    """
    parameter = {"datum": datum} if datum else {}
    antwort = client.get(reverse("wochenplan"), parameter)
    assert antwort.status_code == 200
    return antwort.json()


def setze_zeit(eintrag: m.Fortschritt, tag: date) -> None:
    """Setzt `erledigt_am` (sonst automatisch) auf mittags eines Tages.

    Args:
        eintrag: Der Fortschritt.
        tag: Der gewünschte Tag.
    """
    zeit = timezone.make_aware(datetime(tag.year, tag.month, tag.day, 12))
    m.Fortschritt.objects.filter(pk=eintrag.pk).update(erledigt_am=zeit)


def test_ohne_anmeldung_401(db: None) -> None:
    """Der Plan verlangt eine Anmeldung."""
    assert APIClient().get(reverse("wochenplan")).status_code == 401


@pytest.mark.parametrize(
    ("tag", "montag"),
    [
        (date(2026, 11, 2), date(2026, 11, 2)),
        (date(2026, 11, 4), date(2026, 11, 2)),
        (date(2026, 11, 8), date(2026, 11, 2)),
        (date(2026, 11, 9), date(2026, 11, 9)),
    ],
)
def test_montag_der_woche(tag: date, montag: date) -> None:
    """Sonntag gehört noch zur Woche davor, Montag beginnt die neue."""
    assert montag_der_woche(tag) == montag


def test_fuenf_tage_montag_bis_freitag(client_angemeldet: APIClient) -> None:
    """Die Woche hat fünf Lerntage, das Wochenende ist frei."""
    daten = lade(client_angemeldet, "2026-11-04")

    assert daten["woche_start"] == "2026-11-02"
    assert daten["woche_ende"] == "2026-11-08"
    assert [t["wochentag"] for t in daten["tage"]] == [
        "Montag",
        "Dienstag",
        "Mittwoch",
        "Donnerstag",
        "Freitag",
    ]
    assert daten["vorherige_woche"] == "2026-10-26"
    assert daten["naechste_woche"] == "2026-11-09"


def test_feste_bloecke_montag_bis_donnerstag(client_angemeldet: APIClient) -> None:
    """Vormittag Theorie, Nachmittag Praxis und Englisch."""
    for tag in lade(client_angemeldet, "2026-11-04")["tage"][:4]:
        assert [(b["schluessel"], b["tageszeit"]) for b in tag["bloecke"]] == [
            ("theorie", "vormittag"),
            ("praxis", "nachmittag"),
            ("englisch", "nachmittag"),
        ]


def test_freitag_test_und_wochenauswertung(client_angemeldet: APIClient) -> None:
    """Freitag: Test, Wiederholung, Wochenauswertung und Englisch."""
    freitag = lade(client_angemeldet, "2026-11-04")["tage"][4]

    assert [b["schluessel"] for b in freitag["bloecke"]] == [
        "test",
        "wiederholung",
        "wochenauswertung",
        "englisch",
    ]


def test_heute_markiert(client_angemeldet: APIClient) -> None:
    """Ohne Datum gilt die aktuelle Woche; genau der heutige Wochentag ist markiert."""
    daten = lade(client_angemeldet)
    heute = timezone.localdate()

    assert daten["ist_aktuelle_woche"] is True
    markiert = [t["datum"] for t in daten["tage"] if t["ist_heute"]]
    assert markiert == ([heute.isoformat()] if heute.weekday() < 5 else [])


def test_andere_woche_nicht_aktuell(client_angemeldet: APIClient) -> None:
    """Eine Woche ohne den heutigen Tag ist nicht aktuell und hat keine Markierung."""
    fern = (timezone.localdate() + timedelta(days=21)).isoformat()
    daten = lade(client_angemeldet, fern)

    assert daten["ist_aktuelle_woche"] is False
    assert not any(t["ist_heute"] for t in daten["tage"])


@pytest.mark.parametrize(
    "datum",
    [
        "morgen",
        "2026-13-01",
        "04.11.2026",
        "",
        "0001-01-01",
        "9999-12-31",
        "1999-12-31",
        "2101-01-01",
    ],
)
def test_ungueltiges_datum_400(client_angemeldet: APIClient, datum: str) -> None:
    """Ein Datum, das nicht JJJJ-MM-TT ist, wird abgelehnt."""
    antwort = client_angemeldet.get(reverse("wochenplan"), {"datum": datum})
    assert antwort.status_code == 400


def test_auswertung_leer(client_angemeldet: APIClient) -> None:
    """Ohne Fortschritt: alles 0, keine Trefferquote."""
    assert lade(client_angemeldet, "2026-11-04")["auswertung"] == {
        "abschnitte_gelesen": 0,
        "quizze_bearbeitet": 0,
        "tests_bearbeitet": 0,
        "projekte_erledigt": 0,
        "trefferquote_prozent": None,
    }


def test_auswertung_zaehlt_nur_die_woche(
    client_angemeldet: APIClient, inhalte: Inhalte, nutzer: User
) -> None:
    """Einträge der Woche zählen (Montag 0 Uhr bis Sonntag), andere Wochen nicht."""
    gelesen = m.Fortschritt.objects.create(nutzer=nutzer, abschnitt=inhalte.abschnitt)
    quiz = m.Fortschritt.objects.create(nutzer=nutzer, quiz=inhalte.quiz, punkte=2, max_punkte=3)
    test = m.Fortschritt.objects.create(nutzer=nutzer, test=inhalte.test, punkte=1, max_punkte=1)
    projekt = m.Fortschritt.objects.create(
        nutzer=nutzer, projektaufgabe=inhalte.projekt, punkte=2, max_punkte=2
    )
    setze_zeit(gelesen, date(2026, 11, 2))  # Montag
    setze_zeit(quiz, date(2026, 11, 8))  # Sonntag
    setze_zeit(test, MITTWOCH)
    setze_zeit(projekt, date(2026, 11, 9))  # Folgewoche

    auswertung = lade(client_angemeldet, MITTWOCH.isoformat())["auswertung"]

    assert auswertung == {
        "abschnitte_gelesen": 1,
        "quizze_bearbeitet": 1,
        "tests_bearbeitet": 1,
        "projekte_erledigt": 0,
        "trefferquote_prozent": round(3 / 4 * 100),
    }


def test_auswertung_nur_eigene_daten(
    client_angemeldet: APIClient, inhalte: Inhalte, django_user_model: Any
) -> None:
    """Fortschritt eines anderen Nutzers fließt nicht ein."""
    fremd = django_user_model.objects.create_user("fremd", password="x")
    eintrag = m.Fortschritt.objects.create(nutzer=fremd, abschnitt=inhalte.abschnitt)
    setze_zeit(eintrag, MITTWOCH)

    assert lade(client_angemeldet, MITTWOCH.isoformat())["auswertung"]["abschnitte_gelesen"] == 0
