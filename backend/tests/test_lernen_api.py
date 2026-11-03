"""Tests für die Lern-API: Inhalte lesen, Quiz abgeben, Fortschritt speichern.

Modelle werden als Modul `m` importiert, damit pytest das Modell `Test` nicht sammelt.
"""

import json
from collections.abc import Callable
from typing import Any

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from lernen import models as m
from tests.fabrik import Inhalte, baue_frage

pytestmark = pytest.mark.django_db


def abgeben(client: APIClient, quiz: m.Quiz, antworten: list[dict[str, Any]]) -> Any:
    """Schickt eine Quiz-Abgabe und liefert die Antwort.

    Args:
        client: Angemeldeter API-Client.
        quiz: Das Quiz.
        antworten: Liste aus `{"frage": id, "antwort": id}`.

    Returns:
        Die Antwort des Test-Clients.
    """
    return client.post(
        reverse("quiz-abgabe", kwargs={"pk": quiz.pk}), {"antworten": antworten}, format="json"
    )


# --- Inhalte lesen --------------------------------------------------------------


def test_themenliste(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Die Übersicht listet alle Themen."""
    antwort = client_angemeldet.get(reverse("themen"))

    assert antwort.status_code == 200
    assert [thema["slug"] for thema in antwort.json()] == ["php-laravel"]


def test_thema_mit_gliederung(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Das Thema enthält Phasen mit Lektionen und Projektaufgaben."""
    antwort = client_angemeldet.get(reverse("thema", kwargs={"slug": "php-laravel"}))

    phase = antwort.json()["phasen"][0]
    assert phase["titel"] == "PHP-Basics"
    assert [lektion["titel"] for lektion in phase["lektionen"]] == ["Arrays"]
    assert [projekt["titel"] for projekt in phase["projektaufgaben"]] == ["Einkaufsliste"]


def test_unbekanntes_thema_liefert_404(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Ein unbekannter Slug führt zu 404."""
    antwort = client_angemeldet.get(reverse("thema", kwargs={"slug": "gibt-es-nicht"}))

    assert antwort.status_code == 404


def test_lektion_mit_abschnitten_quellen_quiz_und_test(
    client_angemeldet: APIClient, inhalte: Inhalte
) -> None:
    """Die Lektion liefert Lerntext, Quellen sowie Quiz- und Test-ID."""
    m.Quelle.objects.create(
        lektion=inhalte.lektion, titel="PHP-Handbuch", url="https://www.php.net/"
    )

    daten = client_angemeldet.get(reverse("lektion", kwargs={"pk": inhalte.lektion.pk})).json()

    assert daten["test_id"] == inhalte.test.pk
    assert daten["quellen"] == [{"titel": "PHP-Handbuch", "url": "https://www.php.net/"}]
    assert daten["abschnitte"][0]["inhalt"] == "Text"
    assert daten["abschnitte"][0]["quiz_id"] == inhalte.quiz.pk


def test_lektion_ohne_test_und_quiz(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Fehlen Test oder Quiz, sind die IDs `null` statt eines Fehlers."""
    inhalte.test.delete()
    inhalte.quiz.delete()

    daten = client_angemeldet.get(reverse("lektion", kwargs={"pk": inhalte.lektion.pk})).json()

    assert daten["test_id"] is None
    assert daten["abschnitte"][0]["quiz_id"] is None


def test_lektion_laedt_mit_wenigen_abfragen(
    client_angemeldet: APIClient,
    inhalte: Inhalte,
    django_assert_max_num_queries: Callable[[int], Any],
) -> None:
    """Auch bei vielen Abschnitten bleibt die Zahl der Datenbank-Abfragen klein."""
    for nummer in range(2, 12):
        abschnitt = m.Abschnitt.objects.create(
            lektion=inhalte.lektion, titel=f"A{nummer}", inhalt="x", reihenfolge=nummer
        )
        m.Quiz.objects.create(abschnitt=abschnitt)

    with django_assert_max_num_queries(6):
        client_angemeldet.get(reverse("lektion", kwargs={"pk": inhalte.lektion.pk}))


def test_quiz_verraet_die_loesung_nicht(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Fragen und Antworten kommen ohne `ist_richtig` und ohne Erklärung."""
    baue_frage(inhalte.quiz, 1)

    antwort = client_angemeldet.get(reverse("quiz", kwargs={"pk": inhalte.quiz.pk}))

    assert antwort.status_code == 200
    roh = json.dumps(antwort.json())
    assert "ist_richtig" not in roh
    assert "erklaerung" not in roh
    assert "Weil es so ist." not in roh
    assert len(antwort.json()["fragen"][0]["antworten"]) == 3


# --- Quiz abgeben ---------------------------------------------------------------


def test_abgabe_wertet_aus_und_speichert_fortschritt(
    client_angemeldet: APIClient, inhalte: Inhalte, nutzer: User
) -> None:
    """Richtige und falsche Antworten werden gezählt und als Fortschritt gespeichert."""
    frage1, antworten1 = baue_frage(inhalte.quiz, 1)
    frage2, antworten2 = baue_frage(inhalte.quiz, 2)

    antwort = abgeben(
        client_angemeldet,
        inhalte.quiz,
        [
            {"frage": frage1.pk, "antwort": antworten1[0].pk},
            {"frage": frage2.pk, "antwort": antworten2[1].pk},
        ],
    )

    daten = antwort.json()
    assert antwort.status_code == 200
    assert (daten["punkte"], daten["max_punkte"], daten["bestwert"]) == (1, 2, 1)
    assert daten["fragen"][0]["ist_richtig"] is True
    assert daten["fragen"][1] == {
        "frage_id": frage2.pk,
        "gewaehlte_antwort_id": antworten2[1].pk,
        "richtige_antwort_id": antworten2[0].pk,
        "ist_richtig": False,
        "erklaerung": "Weil es so ist.",
    }
    fortschritt = m.Fortschritt.objects.get(nutzer=nutzer, quiz=inhalte.quiz)
    assert (fortschritt.punkte, fortschritt.max_punkte) == (1, 2)


def test_unbeantwortete_frage_zaehlt_als_falsch(
    client_angemeldet: APIClient, inhalte: Inhalte
) -> None:
    """Fehlt eine Antwort, ist die Frage falsch und `gewaehlte_antwort_id` ist null."""
    frage, _ = baue_frage(inhalte.quiz, 1)

    daten = abgeben(client_angemeldet, inhalte.quiz, []).json()

    assert daten["punkte"] == 0
    assert daten["fragen"][0]["frage_id"] == frage.pk
    assert daten["fragen"][0]["gewaehlte_antwort_id"] is None


def test_bestwert_bleibt_bei_schlechterem_versuch(
    client_angemeldet: APIClient, inhalte: Inhalte, nutzer: User
) -> None:
    """Ein schlechterer zweiter Versuch überschreibt das beste Ergebnis nicht."""
    frage, antworten = baue_frage(inhalte.quiz, 1)
    abgeben(client_angemeldet, inhalte.quiz, [{"frage": frage.pk, "antwort": antworten[0].pk}])

    daten = abgeben(
        client_angemeldet, inhalte.quiz, [{"frage": frage.pk, "antwort": antworten[2].pk}]
    ).json()

    assert (daten["punkte"], daten["bestwert"]) == (0, 1)
    assert m.Fortschritt.objects.get(nutzer=nutzer, quiz=inhalte.quiz).punkte == 1


def test_besserer_versuch_erhoeht_bestwert(
    client_angemeldet: APIClient, inhalte: Inhalte, nutzer: User
) -> None:
    """Ein besserer Versuch ersetzt den gespeicherten Wert."""
    frage, antworten = baue_frage(inhalte.quiz, 1)
    abgeben(client_angemeldet, inhalte.quiz, [{"frage": frage.pk, "antwort": antworten[1].pk}])

    daten = abgeben(
        client_angemeldet, inhalte.quiz, [{"frage": frage.pk, "antwort": antworten[0].pk}]
    ).json()

    assert daten["bestwert"] == 1
    assert m.Fortschritt.objects.filter(nutzer=nutzer, quiz=inhalte.quiz).count() == 1


@pytest.mark.parametrize(
    "fall",
    ["fremde_frage", "fremde_antwort", "doppelte_frage", "kaputte_eingabe", "keine_liste"],
)
def test_ungueltige_abgaben_werden_abgelehnt(
    client_angemeldet: APIClient, inhalte: Inhalte, fall: str
) -> None:
    """Fragen oder Antworten aus anderen Quizzen und kaputte Eingaben führen zu 400."""
    frage, antworten = baue_frage(inhalte.quiz, 1)
    anderes_quiz = m.Quiz.objects.create(
        abschnitt=m.Abschnitt.objects.create(
            lektion=inhalte.lektion, titel="B", inhalt="x", reihenfolge=2
        )
    )
    fremde_frage, fremde_antworten = baue_frage(anderes_quiz, 1)
    eingaben: dict[str, Any] = {
        "fremde_frage": [{"frage": fremde_frage.pk, "antwort": fremde_antworten[0].pk}],
        "fremde_antwort": [{"frage": frage.pk, "antwort": fremde_antworten[0].pk}],
        "doppelte_frage": [
            {"frage": frage.pk, "antwort": antworten[0].pk},
            {"frage": frage.pk, "antwort": antworten[1].pk},
        ],
        "kaputte_eingabe": [{"frage": "eins", "antwort": None}],
        "keine_liste": "alles richtig",
    }

    antwort = abgeben(client_angemeldet, inhalte.quiz, eingaben[fall])

    assert antwort.status_code == 400
    assert not m.Fortschritt.objects.filter(quiz=inhalte.quiz).exists()


def test_quiz_ohne_fragen_kann_nicht_abgegeben_werden(
    client_angemeldet: APIClient, inhalte: Inhalte
) -> None:
    """Ein leeres Quiz liefert 400 statt eines Ergebnisses von 0 von 0."""
    antwort = abgeben(client_angemeldet, inhalte.quiz, [])

    assert antwort.status_code == 400
    assert antwort.json() == {"detail": "Das Quiz hat keine Fragen."}


def test_abgabe_fuer_unbekanntes_quiz_liefert_404(client_angemeldet: APIClient) -> None:
    """Ein nicht vorhandenes Quiz führt zu 404."""
    antwort = client_angemeldet.post(
        reverse("quiz-abgabe", kwargs={"pk": 999}), {"antworten": []}, format="json"
    )

    assert antwort.status_code == 404


# --- Fortschritt ----------------------------------------------------------------


def test_abschnitt_als_gelesen_markieren(
    client_angemeldet: APIClient, inhalte: Inhalte, nutzer: User
) -> None:
    """Gelesen-Markierung wird gespeichert; ein zweiter Aufruf legt nichts doppelt an."""
    url = reverse("abschnitt-gelesen", kwargs={"pk": inhalte.abschnitt.pk})

    erste = client_angemeldet.post(url)
    zweite = client_angemeldet.post(url)

    assert erste.status_code == zweite.status_code == 200
    assert erste.json()["abschnitt"] == inhalte.abschnitt.pk
    assert m.Fortschritt.objects.filter(nutzer=nutzer, abschnitt=inhalte.abschnitt).count() == 1


def test_unbekannter_abschnitt_liefert_404(client_angemeldet: APIClient) -> None:
    """Ein nicht vorhandener Abschnitt führt zu 404."""
    antwort = client_angemeldet.post(reverse("abschnitt-gelesen", kwargs={"pk": 999}))

    assert antwort.status_code == 404


def test_fortschritt_zeigt_nur_eigene_eintraege(
    client_angemeldet: APIClient, inhalte: Inhalte, nutzer: User
) -> None:
    """Fremder Fortschritt ist nicht sichtbar."""
    fremder = User.objects.create_user(username="fremd", password="geheim-789")
    m.Fortschritt.objects.create(nutzer=fremder, abschnitt=inhalte.abschnitt)
    m.Fortschritt.objects.create(nutzer=nutzer, quiz=inhalte.quiz, punkte=2, max_punkte=3)

    daten = client_angemeldet.get(reverse("fortschritt")).json()

    assert len(daten) == 1
    assert (daten[0]["quiz"], daten[0]["punkte"], daten[0]["max_punkte"]) == (
        inhalte.quiz.pk,
        2,
        3,
    )


def test_abgabe_eines_anderen_nutzers_aendert_eigenen_fortschritt_nicht(
    inhalte: Inhalte, nutzer: User
) -> None:
    """Jeder Nutzer hat seinen eigenen Bestwert."""
    frage, antworten = baue_frage(inhalte.quiz, 1)
    fremder = User.objects.create_user(username="fremd", password="geheim-789")
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=fremder).key}")

    abgeben(client, inhalte.quiz, [{"frage": frage.pk, "antwort": antworten[0].pk}])

    assert not m.Fortschritt.objects.filter(nutzer=nutzer).exists()
    assert m.Fortschritt.objects.get(nutzer=fremder).punkte == 1


def test_abgabe_ohne_antworten_feld_wird_abgelehnt(
    client_angemeldet: APIClient, inhalte: Inhalte
) -> None:
    """Fehlt der Schlüssel `antworten`, antwortet die API mit 400 und nennt das Feld."""
    baue_frage(inhalte.quiz, 1)

    antwort = client_angemeldet.post(
        reverse("quiz-abgabe", kwargs={"pk": inhalte.quiz.pk}), {}, format="json"
    )

    assert antwort.status_code == 400
    assert "antworten" in antwort.json()
