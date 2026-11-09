"""Wochen- und Tagesplan mit festen Blöcken und Wochenauswertung.

Der Plan ist fest vorgegeben (docs/LERNPLAN.md, „Tagesstruktur“): fünf Tage pro
Woche, Wochenende frei. Vormittag Theorie, Nachmittag Praxis und Quiz, täglich
Englisch, Freitag Test, Wiederholung und Wochenauswertung. Die Auswertung wird aus
dem Fortschritt berechnet (keine eigene Tabelle), siehe docs/ENTSCHEIDUNGEN.md (B6).

Zum Abarbeiten (Backlog F3) stehen an den Lerntagen konkrete Abschnitte: Montag bis
Donnerstag je `THEORIE_PRO_TAG` Abschnitte der Haupt-Themen in Lernreihenfolge, täglich
ein Englisch-Abschnitt. Der Plan ist fest und beginnt am Lernstart. Was an einem früheren
Tag offen blieb, steht als „nachholen“ da und rutscht nicht nach.
"""

from dataclasses import dataclass, field, replace
from datetime import date, datetime, time, timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from lernen.models import Abschnitt, Fortschritt, Quiz

#: Wochentage auf Deutsch, Index 0 = Montag.
WOCHENTAGE = ("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag")
#: Anzahl der Lerntage pro Woche (Montag bis Freitag).
LERNTAGE = 5
#: Zulässiger Jahresbereich für Anfragen (schützt vor Überlauf bei der Wochenrechnung).
MIN_JAHR = 2000
MAX_JAHR = 2100
#: Index des Freitags (Wochenende der Lernwoche).
FREITAG = 4
#: Theorie-Abschnitte pro Lerntag (Montag bis Donnerstag).
THEORIE_PRO_TAG = 4
#: Anzahl der Tage mit neuen Theorie-Abschnitten (Montag bis Donnerstag).
THEORIE_TAGE = 4
#: Englisch-Abschnitte pro Lerntag (Montag bis Freitag).
ENGLISCH_PRO_TAG = 1
#: Kennung des Englisch-Themas. Es hat einen eigenen täglichen Block.
ENGLISCH_SLUG = "englisch"
#: So viele überfällige Abschnitte listet der Plan höchstens einzeln auf.
MAX_NACHHOLEN = 20

#: Status einer Aufgabe im Plan.
STATUS_ERLEDIGT = "erledigt"
STATUS_NACHHOLEN = "nachholen"
STATUS_OFFEN = "offen"
STATUS_GEPLANT = "geplant"


@dataclass(frozen=True)
class Aufgabe:
    """Ein Abschnitt, der an einem Tag dran ist.

    Attributes:
        abschnitt_id: ID des Abschnitts.
        lektion_id: ID der Lektion (für den Link zur Lektion).
        nummer: Nummer des Abschnitts in der Lektion (1-basiert, für `?abschnitt=`).
        titel: Titel des Abschnitts.
        lektion_titel: Titel der Lektion.
        thema_titel: Titel des Themas.
        erledigt: Ob der Abschnitt gelesen und das Quiz abgegeben ist.
        status: `erledigt`, `nachholen` (Tag vorbei, noch offen), `offen` (heute) oder `geplant`.
        datum: Der Tag, an dem der Abschnitt dran ist.
    """

    abschnitt_id: int
    lektion_id: int
    nummer: int
    titel: str
    lektion_titel: str
    thema_titel: str
    erledigt: bool
    status: str
    datum: date


@dataclass(frozen=True)
class Block:
    """Ein fester Zeitblock des Tages.

    Attributes:
        schluessel: Stabiler Name des Blocks.
        tageszeit: `vormittag` oder `nachmittag`.
        titel: Anzeigename.
        beschreibung: Was in dem Block getan wird.
        dauer: Richtdauer als Text, z. B. „ca. 3 Std.“.
        aufgaben: Die Abschnitte, die in diesem Block dran sind (oft leer).
    """

    schluessel: str
    tageszeit: str
    titel: str
    beschreibung: str
    dauer: str
    aufgaben: list[Aufgabe] = field(default_factory=list)


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
        lernstart: Erster Tag des Plans.
        nachholen: Überfällige, noch offene Abschnitte (älteste zuerst, höchstens `MAX_NACHHOLEN`).
        nachholen_anzahl: Gesamtzahl der überfälligen, noch offenen Abschnitte.
    """

    woche_start: date
    woche_ende: date
    vorherige_woche: date
    naechste_woche: date
    ist_aktuelle_woche: bool
    tage: list[Tag]
    auswertung: Wochenauswertung
    lernstart: date
    nachholen: list[Aufgabe]
    nachholen_anzahl: int


@dataclass(frozen=True)
class _Eintrag:
    """Ein Abschnitt der Lernreihenfolge (nur intern)."""

    abschnitt_id: int
    lektion_id: int
    nummer: int
    titel: str
    lektion_titel: str
    thema_titel: str


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


def _lernreihenfolge(englisch: bool) -> list[_Eintrag]:
    """Liest alle Abschnitte in Lernreihenfolge (Thema, Phase, Lektion, Abschnitt).

    Args:
        englisch: True für die Englisch-Abschnitte, False für alle übrigen Themen.

    Returns:
        Die Abschnitte der gewählten Gruppe in fester Reihenfolge.
    """
    abfrage = (
        Abschnitt.objects.select_related("lektion__phase__thema")
        .defer("inhalt")
        .order_by(
            "lektion__phase__thema__reihenfolge",
            "lektion__phase__reihenfolge",
            "lektion__reihenfolge",
            "reihenfolge",
        )
    )
    if englisch:
        abfrage = abfrage.filter(lektion__phase__thema__slug=ENGLISCH_SLUG)
    else:
        abfrage = abfrage.exclude(lektion__phase__thema__slug=ENGLISCH_SLUG)
    eintraege: list[_Eintrag] = []
    zaehler: dict[int, int] = {}
    for abschnitt in abfrage:
        nummer = zaehler.get(abschnitt.lektion_id, 0) + 1
        zaehler[abschnitt.lektion_id] = nummer
        eintraege.append(
            _Eintrag(
                abschnitt_id=abschnitt.pk,
                lektion_id=abschnitt.lektion_id,
                nummer=nummer,
                titel=abschnitt.titel,
                lektion_titel=abschnitt.lektion.titel,
                thema_titel=abschnitt.lektion.phase.thema.titel,
            )
        )
    return eintraege


def _erledigte_abschnitte(nutzer: User) -> set[int]:
    """Bestimmt die Abschnitte, die gelesen sind und deren Quiz abgegeben ist.

    Args:
        nutzer: Der angemeldete Nutzer.

    Returns:
        Die IDs der erledigten Abschnitte. Ein Abschnitt ohne Quiz zählt, sobald er gelesen ist.
    """
    gelesen = set(
        Fortschritt.objects.filter(nutzer=nutzer, abschnitt__isnull=False).values_list(
            "abschnitt_id", flat=True
        )
    )
    quiz_abgegeben = set(
        Fortschritt.objects.filter(nutzer=nutzer, quiz__isnull=False).values_list(
            "quiz__abschnitt_id", flat=True
        )
    )
    mit_quiz = set(Quiz.objects.values_list("abschnitt_id", flat=True))
    return {a for a in gelesen if a not in mit_quiz or a in quiz_abgegeben}


def _erster_lerntag(lernstart: date, tage_pro_woche: int) -> date:
    """Gibt den ersten Lerntag ab dem Lernstart zurück.

    Args:
        lernstart: Erster Tag des Plans.
        tage_pro_woche: 4 für Montag bis Donnerstag, 5 für Montag bis Freitag.

    Returns:
        Den Lernstart selbst oder den nächsten Wochentag vor `tage_pro_woche`.
    """
    tag = lernstart
    while tag.weekday() >= tage_pro_woche:
        tag += timedelta(days=1)
    return tag


def _tagesnummer(tag: date, lernstart: date, tage_pro_woche: int) -> int | None:
    """Zählt, der wievielte Lerntag ein Tag ist (0 = erster Lerntag).

    Args:
        tag: Das Datum.
        lernstart: Erster Tag des Plans.
        tage_pro_woche: 4 für Montag bis Donnerstag, 5 für Montag bis Freitag.

    Returns:
        Die Nummer des Lerntags oder None, wenn der Tag kein Lerntag ist
        (Wochenende, Freitag bei Theorie oder vor dem Lernstart).
    """
    if tag < lernstart or tag.weekday() >= tage_pro_woche:
        return None
    erster = _erster_lerntag(lernstart, tage_pro_woche)
    wochen = (montag_der_woche(tag) - montag_der_woche(erster)).days // 7
    return wochen * tage_pro_woche + tag.weekday() - erster.weekday()


def _aufgaben_fuer(
    folge: list[_Eintrag],
    nummer: int | None,
    pro_tag: int,
    tag: date,
    heute: date,
    erledigt: set[int],
) -> list[Aufgabe]:
    """Wählt die Abschnitte, die an einem Lerntag dran sind.

    Args:
        folge: Die Lernreihenfolge der Gruppe.
        nummer: Nummer des Lerntags (siehe `_tagesnummer`) oder None.
        pro_tag: Anzahl der Abschnitte pro Lerntag.
        tag: Das Datum des Tages.
        heute: Das heutige Datum.
        erledigt: IDs der erledigten Abschnitte.

    Returns:
        Die Aufgaben des Tages; leer, wenn kein Lerntag oder die Reihenfolge zu Ende ist.
    """
    if nummer is None:
        return []
    aufgaben: list[Aufgabe] = []
    for eintrag in folge[nummer * pro_tag : (nummer + 1) * pro_tag]:
        ist_erledigt = eintrag.abschnitt_id in erledigt
        if ist_erledigt:
            status = STATUS_ERLEDIGT
        elif tag < heute:
            status = STATUS_NACHHOLEN
        elif tag == heute:
            status = STATUS_OFFEN
        else:
            status = STATUS_GEPLANT
        aufgaben.append(
            Aufgabe(
                abschnitt_id=eintrag.abschnitt_id,
                lektion_id=eintrag.lektion_id,
                nummer=eintrag.nummer,
                titel=eintrag.titel,
                lektion_titel=eintrag.lektion_titel,
                thema_titel=eintrag.thema_titel,
                erledigt=ist_erledigt,
                status=status,
                datum=tag,
            )
        )
    return aufgaben


def _ueberfaellig(
    theorie: list[_Eintrag],
    englisch: list[_Eintrag],
    lernstart: date,
    heute: date,
    erledigt: set[int],
) -> list[Aufgabe]:
    """Sammelt alle Abschnitte früherer Lerntage, die noch nicht erledigt sind.

    Args:
        theorie: Lernreihenfolge der Haupt-Themen.
        englisch: Lernreihenfolge Englisch.
        lernstart: Erster Tag des Plans.
        heute: Das heutige Datum.
        erledigt: IDs der erledigten Abschnitte.

    Returns:
        Die überfälligen Aufgaben, älteste zuerst (am gleichen Tag Theorie vor Englisch).
    """
    offen: list[Aufgabe] = []
    tag = lernstart
    while tag < heute:
        for folge, tage, pro_tag in (
            (theorie, THEORIE_TAGE, THEORIE_PRO_TAG),
            (englisch, LERNTAGE, ENGLISCH_PRO_TAG),
        ):
            nummer = _tagesnummer(tag, lernstart, tage)
            offen += [
                a
                for a in _aufgaben_fuer(folge, nummer, pro_tag, tag, heute, erledigt)
                if not a.erledigt
            ]
        tag += timedelta(days=1)
    return offen


def erstelle_wochenplan(nutzer: User, tag: date, heute: date, lernstart: date) -> Wochenplan:
    """Baut den Plan der Woche, in der `tag` liegt.

    Args:
        nutzer: Der angemeldete Nutzer.
        tag: Ein Datum der gewünschten Woche.
        heute: Das heutige Datum (zum Markieren des heutigen Tages).
        lernstart: Erster Tag des Plans (vorher sind keine Abschnitte zugeteilt).

    Returns:
        Die Lernwoche mit fünf Tagen, den zugeteilten Abschnitten, der Liste der
        überfälligen Abschnitte und der Wochenauswertung.
    """
    start = montag_der_woche(tag)
    theorie = _lernreihenfolge(englisch=False)
    englisch = _lernreihenfolge(englisch=True)
    erledigt = _erledigte_abschnitte(nutzer)
    tage: list[Tag] = []
    for i in range(LERNTAGE):
        datum = start + timedelta(days=i)
        zuordnung = {
            "theorie": _aufgaben_fuer(
                theorie,
                _tagesnummer(datum, lernstart, THEORIE_TAGE),
                THEORIE_PRO_TAG,
                datum,
                heute,
                erledigt,
            ),
            "englisch": _aufgaben_fuer(
                englisch,
                _tagesnummer(datum, lernstart, LERNTAGE),
                ENGLISCH_PRO_TAG,
                datum,
                heute,
                erledigt,
            ),
        }
        tage.append(
            Tag(
                datum=datum,
                wochentag=WOCHENTAGE[i],
                ist_heute=datum == heute,
                bloecke=[
                    replace(block, aufgaben=zuordnung.get(block.schluessel, []))
                    for block in _tagesbloecke(i)
                ],
            )
        )
    ueberfaellig = _ueberfaellig(theorie, englisch, lernstart, heute, erledigt)
    return Wochenplan(
        woche_start=start,
        woche_ende=start + timedelta(days=6),
        vorherige_woche=start - timedelta(days=7),
        naechste_woche=start + timedelta(days=7),
        ist_aktuelle_woche=start == montag_der_woche(heute),
        tage=tage,
        auswertung=_auswertung(nutzer, start),
        lernstart=lernstart,
        nachholen=ueberfaellig[:MAX_NACHHOLEN],
        nachholen_anzahl=len(ueberfaellig),
    )
