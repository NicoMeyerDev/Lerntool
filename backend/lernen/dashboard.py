"""Dashboard: Statistiken, XP, Level, Abzeichen und Meilensteine eines Nutzers.

Alles wird aus dem vorhandenen Fortschritt berechnet (keine eigene Tabelle). So
bleibt es konsistent, wenn sich Inhalte oder Regeln ändern. Die Regeln stehen
als Konstanten oben und sind in docs/ENTSCHEIDUNGEN.md (B5) begründet.
"""

from dataclasses import dataclass

from django.contrib.auth.models import User

from lernen.models import Abschnitt, Fortschritt, Projektaufgabe, Quiz, Test, Thema

#: XP für einen gelesenen Abschnitt.
XP_ABSCHNITT = 10
#: XP je richtig beantworteter Quiz-Frage (Bestwert).
XP_PRO_QUIZ_PUNKT = 5
#: XP je richtig beantworteter Test-Frage (Bestwert). Tests zählen doppelt.
XP_PRO_TEST_PUNKT = 10
#: XP für ein abgeschlossenes Projekt.
XP_PROJEKT = 50
#: XP, die für einen Level-Aufstieg nötig sind (jedes Level gleich weit).
XP_PRO_LEVEL = 100

#: Stufen der Meilensteine (aufsteigend): gelesene Abschnitte, bearbeitete Quizze, XP.
_STUFEN_ABSCHNITTE = (10, 25, 50)
_STUFEN_QUIZZE = (5, 15, 30)
_STUFEN_XP = (250, 500, 1000)


@dataclass(frozen=True)
class Statistik:
    """Zählwerte über den Lernstand.

    Attributes:
        abschnitte_gelesen: Gelesene Abschnitte.
        abschnitte_gesamt: Alle Abschnitte.
        quizze_bearbeitet: Quizze mit gespeichertem Ergebnis.
        quizze_gesamt: Alle Quizze.
        tests_bearbeitet: Tests mit gespeichertem Ergebnis.
        tests_gesamt: Alle Tests.
        projekte_erledigt: Abgeschlossene Projektaufgaben.
        projekte_gesamt: Alle Projektaufgaben.
        trefferquote_prozent: Anteil richtiger Antworten in Quizzen und Tests (Bestwerte)
            in Prozent, None solange es noch kein Ergebnis gibt.
    """

    abschnitte_gelesen: int
    abschnitte_gesamt: int
    quizze_bearbeitet: int
    quizze_gesamt: int
    tests_bearbeitet: int
    tests_gesamt: int
    projekte_erledigt: int
    projekte_gesamt: int
    trefferquote_prozent: int | None


@dataclass(frozen=True)
class ThemaStand:
    """Fortschritt in einem Thema.

    Attributes:
        slug: Kurzname des Themas.
        titel: Titel des Themas.
        erledigt: Erledigte Lernschritte (Abschnitte, Quizze, Tests, Projekte).
        gesamt: Alle Lernschritte des Themas.
    """

    slug: str
    titel: str
    erledigt: int
    gesamt: int


@dataclass(frozen=True)
class Abzeichen:
    """Ein Abzeichen, das man einmal verdient.

    Attributes:
        schluessel: Stabiler Name des Abzeichens.
        titel: Anzeigename.
        beschreibung: Wofür es vergeben wird.
        erreicht: Ob der Nutzer es schon hat.
    """

    schluessel: str
    titel: str
    beschreibung: str
    erreicht: bool


@dataclass(frozen=True)
class Meilenstein:
    """Eine Zählmarke auf dem Weg zur nächsten Stufe.

    Attributes:
        schluessel: Stabiler Name des Meilensteins.
        titel: Anzeigename.
        aktuell: Aktueller Wert.
        ziel: Nächste noch nicht erreichte Stufe (bei erreichter letzter Stufe diese).
        erreicht: Ob die letzte Stufe erreicht ist.
    """

    schluessel: str
    titel: str
    aktuell: int
    ziel: int
    erreicht: bool


@dataclass(frozen=True)
class Dashboard:
    """Alles, was die Startseite an Motivation anzeigt.

    Attributes:
        xp: Gesammelte Erfahrungspunkte.
        level: Aktuelles Level (beginnt bei 1).
        xp_im_level: XP seit Beginn des aktuellen Levels.
        xp_pro_level: XP, die ein Level-Aufstieg braucht.
        statistik: Zählwerte.
        themen: Fortschritt je Thema.
        abzeichen: Alle Abzeichen mit Status.
        meilensteine: Alle Meilensteine mit Stand.
    """

    xp: int
    level: int
    xp_im_level: int
    xp_pro_level: int
    statistik: Statistik
    themen: list[ThemaStand]
    abzeichen: list[Abzeichen]
    meilensteine: list[Meilenstein]


def berechne_level(xp: int) -> tuple[int, int]:
    """Berechnet Level und XP innerhalb des Levels.

    Args:
        xp: Gesammelte XP (nicht negativ).

    Returns:
        Das Level (ab 1) und die XP seit Beginn dieses Levels.
    """
    return xp // XP_PRO_LEVEL + 1, xp % XP_PRO_LEVEL


def _meilenstein(schluessel: str, titel: str, aktuell: int, stufen: tuple[int, ...]) -> Meilenstein:
    """Baut einen Meilenstein mit der nächsten offenen Stufe als Ziel.

    Args:
        schluessel: Stabiler Name.
        titel: Anzeigename.
        aktuell: Aktueller Wert.
        stufen: Aufsteigende Stufen.

    Returns:
        Den Meilenstein.
    """
    ziel = next((stufe for stufe in stufen if stufe > aktuell), stufen[-1])
    return Meilenstein(schluessel, titel, aktuell, ziel, aktuell >= stufen[-1])


def _themen_stand(
    erledigt: dict[str, set[int]],
) -> list[ThemaStand]:
    """Zählt je Thema erledigte und alle Lernschritte.

    Args:
        erledigt: IDs erledigter Ziele je Art (`abschnitt`, `quiz`, `test`, `projekt`).

    Returns:
        Eine Zeile je Thema in fester Reihenfolge.
    """
    gesamt: dict[int, int] = {}
    fertig: dict[int, int] = {}
    quellen = {
        "abschnitt": Abschnitt.objects.values_list("id", "lektion__phase__thema_id"),
        "quiz": Quiz.objects.values_list("id", "abschnitt__lektion__phase__thema_id"),
        "test": Test.objects.values_list("id", "lektion__phase__thema_id"),
        "projekt": Projektaufgabe.objects.values_list("id", "phase__thema_id"),
    }
    for art, zeilen in quellen.items():
        for ziel_id, thema_id in zeilen:
            gesamt[thema_id] = gesamt.get(thema_id, 0) + 1
            if ziel_id in erledigt[art]:
                fertig[thema_id] = fertig.get(thema_id, 0) + 1
    return [
        ThemaStand(thema.slug, thema.titel, fertig.get(thema.id, 0), gesamt.get(thema.id, 0))
        for thema in Thema.objects.all()
    ]


def erstelle_dashboard(nutzer: User) -> Dashboard:
    """Berechnet das Dashboard eines Nutzers aus seinem Fortschritt.

    Args:
        nutzer: Der angemeldete Nutzer.

    Returns:
        Statistiken, XP, Level, Themenfortschritt, Abzeichen und Meilensteine.
    """
    eintraege = list(
        Fortschritt.objects.filter(nutzer=nutzer).values(
            "abschnitt_id", "quiz_id", "test_id", "projektaufgabe_id", "punkte", "max_punkte"
        )
    )
    erledigt: dict[str, set[int]] = {
        "abschnitt": {e["abschnitt_id"] for e in eintraege if e["abschnitt_id"] is not None},
        "quiz": {e["quiz_id"] for e in eintraege if e["quiz_id"] is not None},
        "test": {e["test_id"] for e in eintraege if e["test_id"] is not None},
        "projekt": {
            e["projektaufgabe_id"] for e in eintraege if e["projektaufgabe_id"] is not None
        },
    }
    quiz_punkte = sum(e["punkte"] or 0 for e in eintraege if e["quiz_id"] is not None)
    test_punkte = sum(e["punkte"] or 0 for e in eintraege if e["test_id"] is not None)
    ergebnisse = [
        e
        for e in eintraege
        if e["max_punkte"] and (e["quiz_id"] is not None or e["test_id"] is not None)
    ]
    richtig = sum(e["punkte"] or 0 for e in ergebnisse)
    moeglich = sum(e["max_punkte"] or 0 for e in ergebnisse)

    xp = (
        len(erledigt["abschnitt"]) * XP_ABSCHNITT
        + quiz_punkte * XP_PRO_QUIZ_PUNKT
        + test_punkte * XP_PRO_TEST_PUNKT
        + len(erledigt["projekt"]) * XP_PROJEKT
    )
    level, xp_im_level = berechne_level(xp)

    statistik = Statistik(
        abschnitte_gelesen=len(erledigt["abschnitt"]),
        abschnitte_gesamt=Abschnitt.objects.count(),
        quizze_bearbeitet=len(erledigt["quiz"]),
        quizze_gesamt=Quiz.objects.count(),
        tests_bearbeitet=len(erledigt["test"]),
        tests_gesamt=Test.objects.count(),
        projekte_erledigt=len(erledigt["projekt"]),
        projekte_gesamt=Projektaufgabe.objects.count(),
        trefferquote_prozent=round(richtig / moeglich * 100) if moeglich else None,
    )
    volle_punktzahl = any(
        e["max_punkte"] and e["punkte"] == e["max_punkte"]
        for e in eintraege
        if e["quiz_id"] is not None or e["test_id"] is not None
    )
    abzeichen = [
        Abzeichen(
            "erster-schritt",
            "Erster Schritt",
            "Einen Abschnitt gelesen",
            bool(erledigt["abschnitt"]),
        ),
        Abzeichen(
            "volle-punktzahl",
            "Volltreffer",
            "Ein Quiz oder einen Test ohne Fehler",
            volle_punktzahl,
        ),
        Abzeichen("testlauf", "Testlauf", "Den ersten Test abgegeben", bool(erledigt["test"])),
        Abzeichen(
            "projekt-geschafft",
            "Projekt geschafft",
            "Ein Projekt abgeschlossen",
            bool(erledigt["projekt"]),
        ),
        Abzeichen("level-3", "Level 3", "Level 3 erreicht", level >= 3),
    ]
    meilensteine = [
        _meilenstein(
            "abschnitte", "Abschnitte gelesen", len(erledigt["abschnitt"]), _STUFEN_ABSCHNITTE
        ),
        _meilenstein("quizze", "Quizze bearbeitet", len(erledigt["quiz"]), _STUFEN_QUIZZE),
        _meilenstein("xp", "Erfahrungspunkte", xp, _STUFEN_XP),
    ]
    return Dashboard(
        xp=xp,
        level=level,
        xp_im_level=xp_im_level,
        xp_pro_level=XP_PRO_LEVEL,
        statistik=statistik,
        themen=_themen_stand(erledigt),
        abzeichen=abzeichen,
        meilensteine=meilensteine,
    )
