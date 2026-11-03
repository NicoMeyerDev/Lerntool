"""Tests für B4: Testversuche mit Zeitlimit und Projektaufgaben mit Checkliste.

Modelle werden als Modul `m` importiert, damit pytest das Modell `Test` nicht sammelt.
"""

from datetime import timedelta
from typing import Any
from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from lernen import models as m
from lernen.services import TEST_KULANZ_SEKUNDEN
from tests.fabrik import Inhalte, baue_frage

pytestmark = pytest.mark.django_db


def start(client: APIClient, test: m.Test) -> Any:
    """Startet einen Testversuch über die API.

    Args:
        client: Angemeldeter API-Client.
        test: Der Test.

    Returns:
        Die Antwort des Test-Clients.
    """
    return client.post(reverse("test-start", kwargs={"pk": test.pk}))


def abgeben(client: APIClient, test: m.Test, antworten: list[dict[str, Any]]) -> Any:
    """Schickt eine Test-Abgabe.

    Args:
        client: Angemeldeter API-Client.
        test: Der Test.
        antworten: Liste aus `{"frage": id, "antwort": id}`.

    Returns:
        Die Antwort des Test-Clients.
    """
    return client.post(
        reverse("test-abgabe", kwargs={"pk": test.pk}), {"antworten": antworten}, format="json"
    )


def versuch_vor(nutzer: User, test: m.Test, sekunden: int) -> None:
    """Verschiebt den Start des laufenden Versuchs in die Vergangenheit.

    Args:
        nutzer: Der Nutzer.
        test: Der Test.
        sekunden: Wie viele Sekunden der Start zurückliegen soll.
    """
    m.TestVersuch.objects.filter(nutzer=nutzer, test=test, abgegeben_am__isnull=True).update(
        gestartet_am=timezone.now() - timedelta(seconds=sekunden)
    )


# --- Test lesen und starten -----------------------------------------------------


def test_test_zeigt_fragen_ohne_loesung(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Der Test nennt Zeitlimit und Fragen, aber weder Lösung noch Erklärung."""
    baue_frage(inhalte.test, 1)

    antwort = client_angemeldet.get(reverse("test", kwargs={"pk": inhalte.test.pk}))

    assert antwort.status_code == 200
    daten = antwort.json()
    assert daten["zeitlimit_minuten"] == 30
    assert len(daten["fragen"]) == 1
    assert "ist_richtig" not in str(daten)
    assert "erklaerung" not in str(daten)


def test_lektion_nennt_test_id(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Die Lektion verweist auf ihren Test."""
    antwort = client_angemeldet.get(reverse("lektion", kwargs={"pk": inhalte.lektion.pk}))

    assert antwort.json()["test_id"] == inhalte.test.pk


def test_unbekannter_test_liefert_404(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Lesen, Start und Abgabe eines unbekannten Tests führen zu 404."""
    assert client_angemeldet.get(reverse("test", kwargs={"pk": 999})).status_code == 404
    assert client_angemeldet.post(reverse("test-start", kwargs={"pk": 999})).status_code == 404
    antwort = client_angemeldet.post(
        reverse("test-abgabe", kwargs={"pk": 999}), {"antworten": []}, format="json"
    )
    assert antwort.status_code == 404


def test_ohne_anmeldung_401(inhalte: Inhalte) -> None:
    """Alle Test- und Projekt-Endpunkte verlangen eine Anmeldung."""
    client = APIClient()
    adressen = [
        reverse("test", kwargs={"pk": inhalte.test.pk}),
        reverse("projekt", kwargs={"pk": inhalte.projekt.pk}),
    ]
    for adresse in adressen:
        assert client.get(adresse).status_code == 401
    assert client.post(reverse("test-start", kwargs={"pk": inhalte.test.pk})).status_code == 401
    abgabe = reverse("test-abgabe", kwargs={"pk": inhalte.test.pk})
    assert client.post(abgabe, {"antworten": []}, format="json").status_code == 401
    punkt = reverse("projekt-punkt", kwargs={"pk": inhalte.projekt.pk, "punkt_id": 1})
    assert client.put(punkt, {"erledigt": True}, format="json").status_code == 401


def test_paralleler_start_nutzt_laufenden_versuch(
    client_angemeldet: APIClient, inhalte: Inhalte, nutzer: User
) -> None:
    """Gewinnt ein paralleler Start das Rennen, wird dessen Versuch übernommen."""
    vorhandener = m.TestVersuch.objects.create(nutzer=nutzer, test=inhalte.test)

    # Simuliert: Der Versuch wird erst nach der Suche angelegt (Doppelklick).
    with patch("lernen.services._laufender_versuch", return_value=None):
        antwort = start(client_angemeldet, inhalte.test)

    assert antwort.status_code == 200
    assert antwort.json()["versuch_id"] == vorhandener.pk
    assert m.TestVersuch.objects.count() == 1


def test_start_liefert_restzeit(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Der Start liefert eine Restzeit von höchstens 30 Minuten."""
    antwort = start(client_angemeldet, inhalte.test)

    assert antwort.status_code == 200
    assert 29 * 60 < antwort.json()["sekunden_rest"] <= 30 * 60


def test_zweiter_start_setzt_laufenden_versuch_fort(
    client_angemeldet: APIClient, inhalte: Inhalte, nutzer: User
) -> None:
    """Ein erneuter Start (z. B. nach Neuladen) legt keinen zweiten Versuch an."""
    erster = start(client_angemeldet, inhalte.test).json()
    versuch_vor(nutzer, inhalte.test, 600)

    zweiter = start(client_angemeldet, inhalte.test).json()

    assert zweiter["versuch_id"] == erster["versuch_id"]
    assert zweiter["sekunden_rest"] < 21 * 60
    assert m.TestVersuch.objects.count() == 1


def test_abgelaufener_versuch_wird_durch_neuen_ersetzt(
    client_angemeldet: APIClient, inhalte: Inhalte, nutzer: User
) -> None:
    """Ein längst abgelaufener, nie abgegebener Versuch zählt nicht mehr."""
    erster = start(client_angemeldet, inhalte.test).json()
    versuch_vor(nutzer, inhalte.test, 30 * 60 + TEST_KULANZ_SEKUNDEN + 5)

    neu = start(client_angemeldet, inhalte.test).json()

    assert neu["versuch_id"] != erster["versuch_id"]
    assert neu["sekunden_rest"] > 29 * 60
    assert m.TestVersuch.objects.filter(abgegeben_am__isnull=True).count() == 1


def test_kuerzeres_zeitlimit_gilt(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Das Zeitlimit stammt aus dem Test (hier 10 Minuten)."""
    inhalte.test.zeitlimit_minuten = 10
    inhalte.test.save()

    antwort = start(client_angemeldet, inhalte.test)

    assert antwort.json()["sekunden_rest"] <= 10 * 60


# --- Abgabe ---------------------------------------------------------------------


def test_abgabe_wertet_aus_und_speichert_bestwert(
    client_angemeldet: APIClient, inhalte: Inhalte, nutzer: User
) -> None:
    """Rechtzeitige Abgabe: Auswertung mit Lösung, Bestwert im Fortschritt."""
    frage1, antworten1 = baue_frage(inhalte.test, 1)
    frage2, antworten2 = baue_frage(inhalte.test, 2)
    start(client_angemeldet, inhalte.test)

    antwort = abgeben(
        client_angemeldet,
        inhalte.test,
        [
            {"frage": frage1.pk, "antwort": antworten1[0].pk},
            {"frage": frage2.pk, "antwort": antworten2[1].pk},
        ],
    )

    assert antwort.status_code == 200
    daten = antwort.json()
    assert (daten["punkte"], daten["max_punkte"], daten["bestwert"]) == (1, 2, 1)
    assert daten["fragen"][1]["richtige_antwort_id"] == antworten2[0].pk
    fortschritt = m.Fortschritt.objects.get(nutzer=nutzer, test=inhalte.test)
    assert (fortschritt.punkte, fortschritt.max_punkte) == (1, 2)


def test_schlechterer_zweiter_versuch_senkt_bestwert_nicht(
    client_angemeldet: APIClient, inhalte: Inhalte
) -> None:
    """Der Bestwert bleibt erhalten, wenn ein späterer Versuch schlechter ist."""
    frage, antworten = baue_frage(inhalte.test, 1)
    start(client_angemeldet, inhalte.test)
    abgeben(client_angemeldet, inhalte.test, [{"frage": frage.pk, "antwort": antworten[0].pk}])
    start(client_angemeldet, inhalte.test)

    antwort = abgeben(
        client_angemeldet, inhalte.test, [{"frage": frage.pk, "antwort": antworten[1].pk}]
    )

    assert antwort.json()["punkte"] == 0
    assert antwort.json()["bestwert"] == 1


def test_abgabe_beendet_versuch(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Nach der Abgabe braucht es einen neuen Start (sonst 409)."""
    frage, antworten = baue_frage(inhalte.test, 1)
    start(client_angemeldet, inhalte.test)
    eintrag = [{"frage": frage.pk, "antwort": antworten[0].pk}]
    assert abgeben(client_angemeldet, inhalte.test, eintrag).status_code == 200

    zweite = abgeben(client_angemeldet, inhalte.test, eintrag)

    assert zweite.status_code == 409


def test_abgabe_ohne_start_409(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Ohne laufenden Versuch gibt es keine Auswertung und damit keine Lösungen."""
    baue_frage(inhalte.test, 1)

    antwort = abgeben(client_angemeldet, inhalte.test, [])

    assert antwort.status_code == 409
    assert "richtige_antwort_id" not in str(antwort.json())
    assert not m.Fortschritt.objects.exists()


def test_abgabe_nach_ablauf_wird_abgelehnt(
    client_angemeldet: APIClient, inhalte: Inhalte, nutzer: User
) -> None:
    """Nach Zeitlimit plus Kulanz: 409, nichts gespeichert, Versuch beendet."""
    frage, antworten = baue_frage(inhalte.test, 1)
    start(client_angemeldet, inhalte.test)
    versuch_vor(nutzer, inhalte.test, 30 * 60 + TEST_KULANZ_SEKUNDEN + 5)

    antwort = abgeben(
        client_angemeldet, inhalte.test, [{"frage": frage.pk, "antwort": antworten[0].pk}]
    )

    assert antwort.status_code == 409
    assert not m.Fortschritt.objects.exists()
    assert not m.TestVersuch.objects.filter(abgegeben_am__isnull=True).exists()


def test_abgabe_innerhalb_der_kulanz_zaehlt(
    client_angemeldet: APIClient, inhalte: Inhalte, nutzer: User
) -> None:
    """Kurz nach Ablauf (Netzwerkverzögerung beim Auto-Abgeben) wird noch gewertet."""
    frage, antworten = baue_frage(inhalte.test, 1)
    start(client_angemeldet, inhalte.test)
    versuch_vor(nutzer, inhalte.test, 30 * 60 + 5)

    antwort = abgeben(
        client_angemeldet, inhalte.test, [{"frage": frage.pk, "antwort": antworten[0].pk}]
    )

    assert antwort.status_code == 200
    assert antwort.json()["punkte"] == 1


def test_ungueltige_abgabe_beendet_versuch_nicht(
    client_angemeldet: APIClient, inhalte: Inhalte
) -> None:
    """Fremde Fragen → 400, der Versuch läuft weiter."""
    baue_frage(inhalte.test, 1)
    start(client_angemeldet, inhalte.test)

    antwort = abgeben(client_angemeldet, inhalte.test, [{"frage": 9999, "antwort": 1}])

    assert antwort.status_code == 400
    assert m.TestVersuch.objects.filter(abgegeben_am__isnull=True).count() == 1


def test_test_ohne_fragen_400(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Ein Test ohne Fragen lässt sich nicht abgeben."""
    start(client_angemeldet, inhalte.test)

    assert abgeben(client_angemeldet, inhalte.test, []).status_code == 400


def test_doppelte_frage_in_abgabe_400(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Dieselbe Frage zweimal zu beantworten ist ungültig."""
    frage, antworten = baue_frage(inhalte.test, 1)
    start(client_angemeldet, inhalte.test)
    eintrag = {"frage": frage.pk, "antwort": antworten[0].pk}

    assert abgeben(client_angemeldet, inhalte.test, [eintrag, eintrag]).status_code == 400


def test_versuche_zweier_nutzer_sind_getrennt(
    client_angemeldet: APIClient, inhalte: Inhalte
) -> None:
    """Der Versuch eines anderen Nutzers lässt sich nicht abgeben."""
    baue_frage(inhalte.test, 1)
    fremder = User.objects.create_user(username="fremd", password="geheim-123")
    m.TestVersuch.objects.create(nutzer=fremder, test=inhalte.test)

    assert abgeben(client_angemeldet, inhalte.test, []).status_code == 409


# --- Projektaufgaben ------------------------------------------------------------


def baue_punkte(projekt: m.Projektaufgabe, anzahl: int) -> list[m.ProjektPunkt]:
    """Legt Checklisten-Punkte an.

    Args:
        projekt: Die Projektaufgabe.
        anzahl: Anzahl der Punkte.

    Returns:
        Die Punkte in Reihenfolge.
    """
    return [
        m.ProjektPunkt.objects.create(projektaufgabe=projekt, text=f"Punkt {i}", reihenfolge=i)
        for i in range(1, anzahl + 1)
    ]


def haken(client: APIClient, projekt: m.Projektaufgabe, punkt: m.ProjektPunkt, wert: bool) -> Any:
    """Hakt einen Punkt ab oder nimmt den Haken zurück.

    Args:
        client: Angemeldeter API-Client.
        projekt: Die Projektaufgabe.
        punkt: Der Punkt.
        wert: Ob abgehakt sein soll.

    Returns:
        Die Antwort des Test-Clients.
    """
    return client.put(
        reverse("projekt-punkt", kwargs={"pk": projekt.pk, "punkt_id": punkt.pk}),
        {"erledigt": wert},
        format="json",
    )


def test_projekt_zeigt_checkliste(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Das Projekt liefert Aufgabe, Punkte und Stand 0 von n."""
    baue_punkte(inhalte.projekt, 3)

    daten = client_angemeldet.get(reverse("projekt", kwargs={"pk": inhalte.projekt.pk})).json()

    assert daten["titel"] == "Einkaufsliste"
    assert [p["text"] for p in daten["punkte"]] == ["Punkt 1", "Punkt 2", "Punkt 3"]
    assert (daten["erledigt"], daten["gesamt"], daten["abgeschlossen"]) == (0, 3, False)
    assert not any(p["erledigt"] for p in daten["punkte"])


def test_unbekanntes_projekt_404(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Ein unbekanntes Projekt führt zu 404."""
    assert client_angemeldet.get(reverse("projekt", kwargs={"pk": 999})).status_code == 404


def test_punkt_abhaken_zaehlt(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Abhaken erhöht den Zähler; der Haken erscheint im Projekt."""
    punkte = baue_punkte(inhalte.projekt, 3)

    daten = haken(client_angemeldet, inhalte.projekt, punkte[0], True).json()

    assert (daten["erledigt"], daten["gesamt"], daten["abgeschlossen"]) == (1, 3, False)
    assert [p["erledigt"] for p in daten["punkte"]] == [True, False, False]
    assert not m.Fortschritt.objects.exists()


def test_abhaken_ist_wiederholbar(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Zweimal abhaken zählt nur einmal."""
    punkte = baue_punkte(inhalte.projekt, 2)
    haken(client_angemeldet, inhalte.projekt, punkte[0], True)

    daten = haken(client_angemeldet, inhalte.projekt, punkte[0], True).json()

    assert daten["erledigt"] == 1


def test_komplette_checkliste_speichert_fortschritt(
    client_angemeldet: APIClient, inhalte: Inhalte, nutzer: User
) -> None:
    """Sind alle Punkte abgehakt, ist das Projekt erledigt (Fortschritt n von n)."""
    punkte = baue_punkte(inhalte.projekt, 2)
    haken(client_angemeldet, inhalte.projekt, punkte[0], True)

    daten = haken(client_angemeldet, inhalte.projekt, punkte[1], True).json()

    assert daten["abgeschlossen"] is True
    fortschritt = m.Fortschritt.objects.get(nutzer=nutzer, projektaufgabe=inhalte.projekt)
    assert (fortschritt.punkte, fortschritt.max_punkte) == (2, 2)


def test_haken_zuruecknehmen_entfernt_fortschritt(
    client_angemeldet: APIClient, inhalte: Inhalte
) -> None:
    """Wird ein Haken zurückgenommen, gilt das Projekt wieder als offen."""
    punkte = baue_punkte(inhalte.projekt, 2)
    haken(client_angemeldet, inhalte.projekt, punkte[0], True)
    haken(client_angemeldet, inhalte.projekt, punkte[1], True)

    daten = haken(client_angemeldet, inhalte.projekt, punkte[1], False).json()

    assert daten["abgeschlossen"] is False
    assert daten["erledigt"] == 1
    assert not m.Fortschritt.objects.exists()


def test_haken_gehoeren_dem_nutzer(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Haken eines anderen Nutzers erscheinen nicht in der eigenen Checkliste."""
    punkte = baue_punkte(inhalte.projekt, 1)
    fremder = User.objects.create_user(username="fremd", password="geheim-123")
    m.ProjektPunktErledigt.objects.create(nutzer=fremder, punkt=punkte[0])

    daten = client_angemeldet.get(reverse("projekt", kwargs={"pk": inhalte.projekt.pk})).json()

    assert daten["erledigt"] == 0


def test_punkt_eines_anderen_projekts_404(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Ein Punkt lässt sich nur über sein eigenes Projekt abhaken."""
    anderes = m.Projektaufgabe.objects.create(
        phase=inhalte.phase, titel="Anderes", beschreibung="x", reihenfolge=2
    )
    punkt = baue_punkte(anderes, 1)[0]

    assert haken(client_angemeldet, inhalte.projekt, punkt, True).status_code == 404


def test_abhaken_ohne_erledigt_feld_400(client_angemeldet: APIClient, inhalte: Inhalte) -> None:
    """Fehlt `erledigt`, antwortet die API mit 400."""
    punkt = baue_punkte(inhalte.projekt, 1)[0]

    antwort = client_angemeldet.put(
        reverse("projekt-punkt", kwargs={"pk": inhalte.projekt.pk, "punkt_id": punkt.pk}),
        {},
        format="json",
    )

    assert antwort.status_code == 400


def test_projekt_ohne_checkliste_ist_nie_abgeschlossen(
    client_angemeldet: APIClient, inhalte: Inhalte
) -> None:
    """Ohne Punkte gibt es nichts abzuschließen."""
    daten = client_angemeldet.get(reverse("projekt", kwargs={"pk": inhalte.projekt.pk})).json()

    assert (daten["gesamt"], daten["abgeschlossen"]) == (0, False)
