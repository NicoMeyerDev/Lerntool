"""Tests für die Abschnitte im Wochenplan (Backlog F3): Verteilung, Status und Nachholen.

Modelle werden als Modul `m` importiert, damit pytest das Modell `Test` nicht sammelt.
"""

from datetime import date
from typing import Any

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from lernen import models as m
from lernen import wochenplan
from lernen.wochenplan import _tagesnummer

pytestmark = pytest.mark.django_db

#: Lernstart in den Tests: ein Montag.
START = date(2026, 11, 16)


def baue_thema(
    slug: str, reihenfolge: int, anzahl: int, mit_quiz: bool = True
) -> list[m.Abschnitt]:
    """Legt ein Thema mit einer Phase, einer Lektion und mehreren Abschnitten an.

    Args:
        slug: Kennung des Themas.
        reihenfolge: Position des Themas in der Lernreihenfolge.
        anzahl: Anzahl der Abschnitte.
        mit_quiz: Ob jeder Abschnitt ein Quiz bekommt.

    Returns:
        Die Abschnitte in Reihenfolge.
    """
    thema = m.Thema.objects.create(titel=slug.title(), slug=slug, reihenfolge=reihenfolge)
    phase = m.Phase.objects.create(thema=thema, titel="Phase", slug="phase", reihenfolge=1)
    lektion = m.Lektion.objects.create(
        phase=phase, titel=f"Lektion {slug}", slug="lektion", reihenfolge=1
    )
    abschnitte = [
        m.Abschnitt.objects.create(
            lektion=lektion, titel=f"{slug} {i}", inhalt="Text", reihenfolge=i
        )
        for i in range(1, anzahl + 1)
    ]
    if mit_quiz:
        for abschnitt in abschnitte:
            m.Quiz.objects.create(abschnitt=abschnitt)
    return abschnitte


@pytest.fixture
def inhalt() -> dict[str, list[m.Abschnitt]]:
    """Zwölf Haupt-Abschnitte (PHP) und fünf Englisch-Abschnitte."""
    return {"php": baue_thema("php", 1, 12), "englisch": baue_thema("englisch", 2, 5)}


@pytest.fixture(autouse=True)
def lernstart(settings: Any) -> None:
    """Setzt den Lernstart der Tests auf einen Montag."""
    settings.LERNSTART = START


def setze_heute(monkeypatch: pytest.MonkeyPatch, tag: date) -> None:
    """Legt fest, welcher Tag „heute“ ist.

    Die View ruft `timezone.localdate()` über das Modul auf. Würde sie `localdate` direkt
    importieren, griffe dieser Patch nicht mehr, und die Tests würden still falsch laufen.

    Args:
        monkeypatch: Der pytest-Monkeypatch.
        tag: Das heutige Datum im Test.
    """
    monkeypatch.setattr(timezone, "localdate", lambda: tag)


def lade(client: APIClient, datum: str) -> Any:
    """Ruft den Wochenplan der Woche mit `datum` ab.

    Args:
        client: Angemeldeter API-Client.
        datum: Ein Datum der Woche (JJJJ-MM-TT).

    Returns:
        Den JSON-Inhalt.
    """
    antwort = client.get(reverse("wochenplan"), {"datum": datum})
    assert antwort.status_code == 200
    return antwort.json()


def aufgaben(tag: dict[str, Any], schluessel: str) -> list[dict[str, Any]]:
    """Liefert die Aufgaben eines Blocks eines Tages.

    Args:
        tag: Ein Tag aus dem Plan.
        schluessel: Schlüssel des Blocks (`theorie` oder `englisch`).

    Returns:
        Die Aufgaben oder eine leere Liste, wenn der Tag den Block nicht hat.
    """
    for block in tag["bloecke"]:
        if block["schluessel"] == schluessel:
            return list(block["aufgaben"])
    return []


def titel(liste: list[dict[str, Any]]) -> list[str]:
    """Gibt die Titel einer Aufgabenliste zurück."""
    return [a["titel"] for a in liste]


def erledige(nutzer: User, abschnitt: m.Abschnitt, mit_quiz: bool = True) -> None:
    """Markiert einen Abschnitt als gelesen und gibt (optional) sein Quiz ab.

    Args:
        nutzer: Der Nutzer.
        abschnitt: Der Abschnitt.
        mit_quiz: Ob auch das Quiz abgegeben wird.
    """
    m.Fortschritt.objects.create(nutzer=nutzer, abschnitt=abschnitt)
    if mit_quiz:
        m.Fortschritt.objects.create(nutzer=nutzer, quiz=abschnitt.quiz, punkte=1, max_punkte=1)


def test_vier_abschnitte_je_tag_montag_bis_donnerstag(
    client_angemeldet: APIClient, inhalt: dict[str, list[m.Abschnitt]], monkeypatch: Any
) -> None:
    """Montag 1 bis 4, Dienstag 5 bis 8, Mittwoch 9 bis 12, danach ist die Folge zu Ende."""
    setze_heute(monkeypatch, START)

    tage = lade(client_angemeldet, "2026-11-16")["tage"]

    assert titel(aufgaben(tage[0], "theorie")) == [f"php {i}" for i in (1, 2, 3, 4)]
    assert titel(aufgaben(tage[1], "theorie")) == [f"php {i}" for i in (5, 6, 7, 8)]
    assert titel(aufgaben(tage[2], "theorie")) == [f"php {i}" for i in (9, 10, 11, 12)]
    assert aufgaben(tage[3], "theorie") == []


def test_freitag_hat_keine_neue_theorie(
    client_angemeldet: APIClient, inhalt: dict[str, list[m.Abschnitt]], monkeypatch: Any
) -> None:
    """Freitag ist Test und Wiederholung: keine Theorie-Abschnitte, aber Englisch."""
    setze_heute(monkeypatch, START)

    freitag = lade(client_angemeldet, "2026-11-16")["tage"][4]

    assert all(b["aufgaben"] == [] for b in freitag["bloecke"] if b["schluessel"] != "englisch")
    assert titel(aufgaben(freitag, "englisch")) == ["englisch 5"]


def test_taeglich_ein_englisch_abschnitt(
    client_angemeldet: APIClient, inhalt: dict[str, list[m.Abschnitt]], monkeypatch: Any
) -> None:
    """Montag bis Freitag je ein Englisch-Abschnitt in Reihenfolge."""
    setze_heute(monkeypatch, START)

    tage = lade(client_angemeldet, "2026-11-16")["tage"]

    assert [titel(aufgaben(t, "englisch")) for t in tage] == [
        ["englisch 1"],
        ["englisch 2"],
        ["englisch 3"],
        ["englisch 4"],
        ["englisch 5"],
    ]


def test_englisch_steht_nicht_in_der_theorie(
    client_angemeldet: APIClient, inhalt: dict[str, list[m.Abschnitt]], monkeypatch: Any
) -> None:
    """Die Theorie-Folge enthält nur die Haupt-Themen."""
    setze_heute(monkeypatch, START)

    tage = lade(client_angemeldet, "2026-11-16")["tage"]

    alle = [t for tag in tage for t in titel(aufgaben(tag, "theorie"))]
    assert all(name.startswith("php") for name in alle)


def test_zweite_woche_setzt_die_folge_fort(client_angemeldet: APIClient, monkeypatch: Any) -> None:
    """In der zweiten Woche geht es mit dem 17. Abschnitt weiter (4 Tage x 4 Abschnitte)."""
    baue_thema("php", 1, 20)
    setze_heute(monkeypatch, START)

    tage = lade(client_angemeldet, "2026-11-23")["tage"]

    assert titel(aufgaben(tage[0], "theorie")) == [f"php {i}" for i in (17, 18, 19, 20)]


def test_vor_dem_lernstart_nichts_zugeteilt(
    client_angemeldet: APIClient, inhalt: dict[str, list[m.Abschnitt]], monkeypatch: Any
) -> None:
    """Die Woche vor dem Lernstart hat keine Abschnitte; der Plan nennt den Lernstart."""
    setze_heute(monkeypatch, date(2026, 11, 12))

    daten = lade(client_angemeldet, "2026-11-09")

    assert daten["lernstart"] == "2026-11-16"
    assert all(b["aufgaben"] == [] for t in daten["tage"] for b in t["bloecke"])
    assert daten["nachholen_anzahl"] == 0


def test_lernstart_mitten_in_der_woche(
    client_angemeldet: APIClient,
    inhalt: dict[str, list[m.Abschnitt]],
    monkeypatch: Any,
    settings: Any,
) -> None:
    """Beginnt der Plan an einem Mittwoch, ist der Mittwoch der erste Lerntag mit Abschnitt 1."""
    settings.LERNSTART = date(2026, 11, 18)
    setze_heute(monkeypatch, date(2026, 11, 18))

    tage = lade(client_angemeldet, "2026-11-16")["tage"]

    assert aufgaben(tage[0], "theorie") == []
    assert aufgaben(tage[1], "theorie") == []
    assert titel(aufgaben(tage[2], "theorie")) == [f"php {i}" for i in (1, 2, 3, 4)]
    assert titel(aufgaben(tage[3], "theorie")) == [f"php {i}" for i in (5, 6, 7, 8)]
    assert titel(aufgaben(tage[2], "englisch")) == ["englisch 1"]


def test_lernstart_am_wochenende_beginnt_am_montag(
    client_angemeldet: APIClient,
    inhalt: dict[str, list[m.Abschnitt]],
    monkeypatch: Any,
    settings: Any,
) -> None:
    """Ein Lernstart am Samstag führt zum ersten Lerntag am folgenden Montag."""
    settings.LERNSTART = date(2026, 11, 14)
    setze_heute(monkeypatch, date(2026, 11, 16))

    tage = lade(client_angemeldet, "2026-11-16")["tage"]

    assert titel(aufgaben(tage[0], "theorie")) == [f"php {i}" for i in (1, 2, 3, 4)]


def test_nummer_zaehlt_abschnitte_in_der_lektion(
    client_angemeldet: APIClient, inhalt: dict[str, list[m.Abschnitt]], monkeypatch: Any
) -> None:
    """`nummer` ist die Position in der Lektion (für `?abschnitt=`), die Lektion ist verlinkbar."""
    setze_heute(monkeypatch, START)

    erste = aufgaben(lade(client_angemeldet, "2026-11-16")["tage"][1], "theorie")[0]

    assert erste["nummer"] == 5
    assert erste["lektion_id"] == inhalt["php"][4].lektion_id
    assert erste["abschnitt_id"] == inhalt["php"][4].pk
    assert erste["lektion_titel"] == "Lektion php"
    assert erste["thema_titel"] == "Php"


def test_status_heute_offen_vergangen_nachholen_zukunft_geplant(
    client_angemeldet: APIClient, inhalt: dict[str, list[m.Abschnitt]], monkeypatch: Any
) -> None:
    """Status nach Tag: vorbei und offen = nachholen, heute = offen, später = geplant."""
    setze_heute(monkeypatch, date(2026, 11, 17))

    tage = lade(client_angemeldet, "2026-11-16")["tage"]

    assert {a["status"] for a in aufgaben(tage[0], "theorie")} == {"nachholen"}
    assert {a["status"] for a in aufgaben(tage[1], "theorie")} == {"offen"}
    assert {a["status"] for a in aufgaben(tage[2], "theorie")} == {"geplant"}


def test_erledigt_nur_mit_lesen_und_quiz(
    client_angemeldet: APIClient,
    nutzer: User,
    inhalt: dict[str, list[m.Abschnitt]],
    monkeypatch: Any,
) -> None:
    """Gelesen allein genügt nicht, erst mit abgegebenem Quiz gilt der Abschnitt als erledigt."""
    setze_heute(monkeypatch, START)
    php = inhalt["php"]
    erledige(nutzer, php[0])
    erledige(nutzer, php[1], mit_quiz=False)
    m.Fortschritt.objects.create(nutzer=nutzer, quiz=php[2].quiz, punkte=1, max_punkte=1)

    montag = aufgaben(lade(client_angemeldet, "2026-11-16")["tage"][0], "theorie")

    assert [(a["erledigt"], a["status"]) for a in montag] == [
        (True, "erledigt"),
        (False, "offen"),
        (False, "offen"),
        (False, "offen"),
    ]


def test_abschnitt_ohne_quiz_zaehlt_nach_dem_lesen(
    client_angemeldet: APIClient, nutzer: User, monkeypatch: Any
) -> None:
    """Hat ein Abschnitt kein Quiz, reicht das Lesen."""
    abschnitte = baue_thema("php", 1, 4, mit_quiz=False)
    setze_heute(monkeypatch, START)
    m.Fortschritt.objects.create(nutzer=nutzer, abschnitt=abschnitte[0])

    montag = aufgaben(lade(client_angemeldet, "2026-11-16")["tage"][0], "theorie")

    assert montag[0]["erledigt"] is True
    assert montag[1]["erledigt"] is False


def test_nachholen_listet_offene_abschnitte_frueherer_tage(
    client_angemeldet: APIClient,
    nutzer: User,
    inhalt: dict[str, list[m.Abschnitt]],
    monkeypatch: Any,
) -> None:
    """Am Mittwoch sind Montag und Dienstag vorbei: alles Offene davon steht unter nachholen."""
    setze_heute(monkeypatch, date(2026, 11, 18))
    erledige(nutzer, inhalt["php"][0])

    daten = lade(client_angemeldet, "2026-11-18")

    # Montag: 3 Theorie + 1 Englisch offen (php 1 ist erledigt), Dienstag: 4 Theorie + 1 Englisch.
    assert daten["nachholen_anzahl"] == 9
    assert titel(daten["nachholen"]) == [
        "php 2",
        "php 3",
        "php 4",
        "englisch 1",
        "php 5",
        "php 6",
        "php 7",
        "php 8",
        "englisch 2",
    ]
    assert all(a["status"] == "nachholen" for a in daten["nachholen"])


def test_nachholen_wird_kleiner_wenn_erledigt(
    client_angemeldet: APIClient,
    nutzer: User,
    inhalt: dict[str, list[m.Abschnitt]],
    monkeypatch: Any,
) -> None:
    """Erledigte Abschnitte verschwinden aus der Nachhol-Liste und der Plan rutscht nicht nach."""
    setze_heute(monkeypatch, date(2026, 11, 18))
    vorher = lade(client_angemeldet, "2026-11-18")["nachholen_anzahl"]

    erledige(nutzer, inhalt["php"][0])
    daten = lade(client_angemeldet, "2026-11-18")

    assert daten["nachholen_anzahl"] == vorher - 1
    assert titel(aufgaben(daten["tage"][2], "theorie")) == [f"php {i}" for i in (9, 10, 11, 12)]


def test_nachholen_ist_in_jeder_woche_gleich(
    client_angemeldet: APIClient, inhalt: dict[str, list[m.Abschnitt]], monkeypatch: Any
) -> None:
    """Die Nachhol-Liste hängt an „heute“, nicht an der angezeigten Woche."""
    setze_heute(monkeypatch, date(2026, 11, 18))

    aktuell = lade(client_angemeldet, "2026-11-18")
    spaeter = lade(client_angemeldet, "2026-12-02")

    assert spaeter["nachholen"] == aktuell["nachholen"]
    assert spaeter["nachholen_anzahl"] == aktuell["nachholen_anzahl"]


def test_nachholen_ist_begrenzt(
    client_angemeldet: APIClient,
    inhalt: dict[str, list[m.Abschnitt]],
    monkeypatch: Any,
) -> None:
    """Die Liste nennt höchstens MAX_NACHHOLEN Einträge, die Anzahl bleibt vollständig."""
    monkeypatch.setattr("lernen.wochenplan.MAX_NACHHOLEN", 3)
    setze_heute(monkeypatch, date(2026, 11, 20))

    daten = lade(client_angemeldet, "2026-11-20")

    assert len(daten["nachholen"]) == 3
    assert daten["nachholen_anzahl"] > 3
    assert titel(daten["nachholen"]) == ["php 1", "php 2", "php 3"]


def test_nichts_zu_tun_ohne_inhalte(client_angemeldet: APIClient, monkeypatch: Any) -> None:
    """Ohne Lerninhalte bleibt der Plan leer und es gibt nichts nachzuholen."""
    setze_heute(monkeypatch, date(2026, 11, 18))

    daten = lade(client_angemeldet, "2026-11-18")

    assert daten["nachholen"] == []
    assert daten["nachholen_anzahl"] == 0
    assert all(b["aufgaben"] == [] for t in daten["tage"] for b in t["bloecke"])


def test_aufgaben_nur_vom_eigenen_fortschritt(
    client_angemeldet: APIClient,
    inhalt: dict[str, list[m.Abschnitt]],
    monkeypatch: Any,
) -> None:
    """Fortschritt eines anderen Nutzers zählt nicht."""
    fremder = User.objects.create_user(username="fremd", password="Anderes-Passwort-2026!")
    erledige(fremder, inhalt["php"][0])
    setze_heute(monkeypatch, START)

    montag = aufgaben(lade(client_angemeldet, "2026-11-16")["tage"][0], "theorie")

    assert montag[0]["erledigt"] is False


@pytest.mark.parametrize(
    ("tag", "lernstart", "tage_pro_woche", "erwartet"),
    [
        (date(2026, 11, 16), date(2026, 11, 16), 4, 0),
        (date(2026, 11, 19), date(2026, 11, 16), 4, 3),
        (date(2026, 11, 20), date(2026, 11, 16), 4, None),  # Freitag hat keine Theorie
        (date(2026, 11, 20), date(2026, 11, 16), 5, 4),
        (date(2026, 11, 21), date(2026, 11, 16), 5, None),  # Samstag
        (date(2026, 11, 23), date(2026, 11, 16), 4, 4),  # zweite Woche
        (date(2026, 11, 23), date(2026, 11, 16), 5, 5),
        (date(2026, 11, 13), date(2026, 11, 16), 4, None),  # vor dem Lernstart
        (date(2026, 11, 18), date(2026, 11, 18), 4, 0),  # Start am Mittwoch
        (date(2026, 11, 19), date(2026, 11, 18), 4, 1),
        (date(2026, 11, 23), date(2026, 11, 18), 4, 2),
        (date(2026, 11, 23), date(2026, 11, 20), 4, 0),  # Start am Freitag: Theorie ab Montag
        (date(2026, 11, 20), date(2026, 11, 20), 5, 0),  # Start am Freitag: Englisch am Freitag
        (date(2026, 11, 23), date(2026, 11, 20), 5, 1),
        (date(2026, 11, 16), date(2026, 11, 14), 4, 0),  # Start am Samstag
    ],
)
def test_tagesnummer(tag: date, lernstart: date, tage_pro_woche: int, erwartet: int | None) -> None:
    """Die Zählung der Lerntage gilt über Wochen, Wochenenden und beliebige Starttage."""
    assert _tagesnummer(tag, lernstart, tage_pro_woche) == erwartet


def test_englisch_zaehlt_fuenf_pro_woche(client_angemeldet: APIClient, monkeypatch: Any) -> None:
    """In der zweiten Woche beginnt Englisch mit dem 6. Abschnitt (5 Lerntage pro Woche)."""
    baue_thema("php", 1, 4)
    baue_thema("englisch", 2, 10)
    setze_heute(monkeypatch, START)

    tage = lade(client_angemeldet, "2026-11-23")["tage"]

    assert [titel(aufgaben(t, "englisch")) for t in tage[:2]] == [["englisch 6"], ["englisch 7"]]


def test_lernstart_am_freitag(
    client_angemeldet: APIClient, monkeypatch: Any, settings: Any
) -> None:
    """Start am Freitag: Englisch beginnt am Freitag, die Theorie am folgenden Montag."""
    settings.LERNSTART = date(2026, 11, 20)
    baue_thema("php", 1, 8)
    baue_thema("englisch", 2, 6)
    setze_heute(monkeypatch, date(2026, 11, 20))

    woche1 = lade(client_angemeldet, "2026-11-16")["tage"]
    woche2 = lade(client_angemeldet, "2026-11-23")["tage"]

    assert all(aufgaben(t, "theorie") == [] for t in woche1)
    assert titel(aufgaben(woche1[4], "englisch")) == ["englisch 1"]
    assert titel(aufgaben(woche2[0], "theorie")) == [f"php {i}" for i in (1, 2, 3, 4)]
    assert titel(aufgaben(woche2[0], "englisch")) == ["englisch 2"]


def test_standardgrenze_fuer_nachholen() -> None:
    """Standardmäßig werden höchstens 20 überfällige Abschnitte einzeln aufgelistet."""
    assert wochenplan.MAX_NACHHOLEN == 20


def test_lange_pause_bleibt_begrenzt(
    client_angemeldet: APIClient, monkeypatch: Any, settings: Any
) -> None:
    """Nach langer Pause werden alle gezählt, aber nur 20 aufgelistet."""
    settings.LERNSTART = date(2026, 1, 5)
    baue_thema("php", 1, 100)
    setze_heute(monkeypatch, date(2026, 11, 20))

    daten = lade(client_angemeldet, "2026-11-20")

    assert daten["nachholen_anzahl"] == 100
    assert len(daten["nachholen"]) == 20
    assert titel(daten["nachholen"])[0] == "php 1"


def test_abfragen_wachsen_nicht_mit_den_inhalten(
    client_angemeldet: APIClient,
    inhalt: dict[str, list[m.Abschnitt]],
    monkeypatch: Any,
    django_assert_max_num_queries: Any,
) -> None:
    """Der Plan braucht eine feste, kleine Zahl von Abfragen (keine Abfrage je Abschnitt)."""
    baue_thema("devsecops", 3, 60)
    setze_heute(monkeypatch, date(2026, 11, 20))

    with django_assert_max_num_queries(12):
        antwort = client_angemeldet.get(reverse("wochenplan"), {"datum": "2026-11-20"})

    assert antwort.status_code == 200
