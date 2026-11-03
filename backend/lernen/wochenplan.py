"""Wochen- und Tagesplan mit festen Blöcken und Wochenauswertung.

Der Plan ist fest vorgegeben (docs/LERNPLAN.md, „Tagesstruktur“): fünf Tage pro
Woche, Wochenende frei. Vormittag Theorie, Nachmittag Praxis und Quiz, täglich
Englisch, Freitag Test, Wiederholung und Wochenauswertung. Die Auswertung wird aus
dem Fortschritt berechnet (keine eigene Tabelle), siehe docs/ENTSCHEIDUNGEN.md (B6).
"""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from lernen.models import Fortschritt

#: Wochentage auf Deutsch, Index 0 = Montag.
WOCHENTAGE = ("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag")
#: Anzahl der Lerntage pro Woche (Montag bis Freitag).
LERNTAGE = 5
#: Zulässiger Jahresbereich für Anfragen (schützt vor Überlauf bei der Wochenrechnung).
MIN_JAHR = 2000
MAX_JAHR = 2100
#: Index des Freitags (Wochenende der Lernwoche).
FREITAG = 4


@dataclass(frozen=True)
class Block:
    """Ein fester Zeitblock des Tages.

    Attributes:
        schluessel: Stabiler Name des Blocks.
        tageszeit: `vormittag` oder `nachmittag`.
        titel: Anzeigename.
        beschreibung: Was in dem Block getan wird.
        dauer: Richtdauer als Text, z. B. „ca. 3 Std.“.
    """

    schluessel: str
    tageszeit: str
    titel: str
    beschreibung: str
    dauer: str


@dataclass(frozen=True)
class Tag:
    """Ein Lerntag mit seinen Blöcken.

    Attributes:
        datum: Kalenderdatum.
        wochentag: Deutscher Name des Wochentags.
        ist_heute: Ob der Tag der heutige ist.
        bloecke: Die Blöcke des Tages in zeitlicher Reihenfolge.
    """

    datum: date
    wochentag: str
    ist_heute: bool
    bloecke: list[Block]


@dataclass(frozen=True)
class Wochenauswertung:
    """Was in der Woche bearbeitet wurde.

    Gezählt wird, was in der Woche zuletzt gespeichert wurde (ein Eintrag zählt
    mit seinem letzten Stand, siehe ENTSCHEIDUNGEN B6).

    Attributes:
        abschnitte_gelesen: In der Woche als gelesen markierte Abschnitte.
        quizze_bearbeitet: In der Woche abgegebene Quizze.
        tests_bearbeitet: In der Woche abgegebene Tests.
        projekte_erledigt: In der Woche abgeschlossene Projekte.
        trefferquote_prozent: Trefferquote der Quizze und Tests der Woche, None ohne Ergebnis.
    """

    abschnitte_gelesen: int
    quizze_bearbeitet: int
    tests_bearbeitet: int
    projekte_erledigt: int
    trefferquote_prozent: int | None


@dataclass(frozen=True)
class Wochenplan:
    """Eine Lernwoche.

    Attributes:
        woche_start: Montag der Woche.
        woche_ende: Sonntag der Woche.
        vorherige_woche: Montag der Vorwoche.
        naechste_woche: Montag der Folgewoche.
        ist_aktuelle_woche: Ob die Woche die heutige enthält.
        tage: Die fünf Lerntage.
        auswertung: Die Wochenauswertung.
    """

    woche_start: date
    woche_ende: date
    vorherige_woche: date
    naechste_woche: date
    ist_aktuelle_woche: bool
    tage: list[Tag]
    auswertung: Wochenauswertung


def _tagesbloecke(wochentag: int) -> list[Block]:
    """Liefert die festen Blöcke für einen Wochentag.

    Args:
        wochentag: 0 = Montag bis 4 = Freitag.

    Returns:
        Die Blöcke: Montag bis Donnerstag Theorie, Praxis und Englisch; Freitag Test,
        Wiederholung, Wochenauswertung und Englisch.
    """
    englisch = Block(
        "englisch", "nachmittag", "Englisch", "Hören, Lesen und Schreiben üben.", "30–45 Min."
    )
    if wochentag == FREITAG:
        return [
            Block(
                "test",
                "vormittag",
                "Test",
                "Test zum Themenfeld der Woche (höchstens 30 Min.).",
                "ca. 1 Std.",
            ),
            Block(
                "wiederholung",
                "vormittag",
                "Wiederholung",
                "Schwache Stellen der Woche noch einmal durchgehen.",
                "ca. 2 Std.",
            ),
            Block(
                "wochenauswertung",
                "nachmittag",
                "Wochenauswertung",
                "Rückblick: Was lief gut, was kommt nächste Woche dran?",
                "ca. 1 Std.",
            ),
            englisch,
        ]
    return [
        Block(
            "theorie",
            "vormittag",
            "Theorie",
            "Lektion lesen, danach das Quiz zum Abschnitt.",
            "ca. 3 Std.",
        ),
        Block(
            "praxis",
            "nachmittag",
            "Praxis und Quiz",
            "Das Gelernte selbst anwenden, kleine Aufgaben lösen.",
            "ca. 2–3 Std.",
        ),
        englisch,
    ]


def montag_der_woche(tag: date) -> date:
    """Gibt den Montag der Woche zurück, in der ein Datum liegt.

    Args:
        tag: Ein beliebiges Datum.

    Returns:
        Den Montag derselben Woche.
    """
    return tag - timedelta(days=tag.weekday())


def _auswertung(nutzer: User, start: date) -> Wochenauswertung:
    """Zählt die Fortschritts-Einträge der Woche.

    Args:
        nutzer: Der angemeldete Nutzer.
        start: Montag der Woche.

    Returns:
        Die Zahlen der Woche (Montag 0 Uhr bis einschließlich Sonntag, Ortszeit).
    """
    zone = timezone.get_current_timezone()
    von = timezone.make_aware(datetime.combine(start, time.min), zone)
    bis = von + timedelta(days=7)
    eintraege = list(
        Fortschritt.objects.filter(nutzer=nutzer, erledigt_am__gte=von, erledigt_am__lt=bis).values(
            "abschnitt_id", "quiz_id", "test_id", "projektaufgabe_id", "punkte", "max_punkte"
        )
    )
    ergebnisse = [
        e
        for e in eintraege
        if e["max_punkte"] and (e["quiz_id"] is not None or e["test_id"] is not None)
    ]
    richtig = sum(e["punkte"] or 0 for e in ergebnisse)
    moeglich = sum(e["max_punkte"] or 0 for e in ergebnisse)
    return Wochenauswertung(
        abschnitte_gelesen=sum(e["abschnitt_id"] is not None for e in eintraege),
        quizze_bearbeitet=sum(e["quiz_id"] is not None for e in eintraege),
        tests_bearbeitet=sum(e["test_id"] is not None for e in eintraege),
        projekte_erledigt=sum(e["projektaufgabe_id"] is not None for e in eintraege),
        trefferquote_prozent=round(richtig / moeglich * 100) if moeglich else None,
    )


def erstelle_wochenplan(nutzer: User, tag: date, heute: date) -> Wochenplan:
    """Baut den Plan der Woche, in der `tag` liegt.

    Args:
        nutzer: Der angemeldete Nutzer.
        tag: Ein Datum der gewünschten Woche.
        heute: Das heutige Datum (zum Markieren des heutigen Tages).

    Returns:
        Die Lernwoche mit fünf Tagen und der Wochenauswertung.
    """
    start = montag_der_woche(tag)
    tage = [
        Tag(
            datum=start + timedelta(days=i),
            wochentag=WOCHENTAGE[i],
            ist_heute=start + timedelta(days=i) == heute,
            bloecke=_tagesbloecke(i),
        )
        for i in range(LERNTAGE)
    ]
    return Wochenplan(
        woche_start=start,
        woche_ende=start + timedelta(days=6),
        vorherige_woche=start - timedelta(days=7),
        naechste_woche=start + timedelta(days=7),
        ist_aktuelle_woche=start == montag_der_woche(heute),
        tage=tage,
        auswertung=_auswertung(nutzer, start),
    )
