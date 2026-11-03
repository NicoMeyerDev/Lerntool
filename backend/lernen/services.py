"""Geschäftslogik der Lern-App: Quiz und Tests auswerten, Projekte abhaken, Fortschritt."""

import logging
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.utils import timezone

from lernen.models import (
    Abschnitt,
    Fortschritt,
    Frage,
    Projektaufgabe,
    ProjektPunkt,
    ProjektPunktErledigt,
    Quiz,
    Test,
    TestVersuch,
)

logger = logging.getLogger(__name__)

#: Kulanz in Sekunden für Netzwerk und Uhren: So lange nach Ablauf zählt eine Abgabe noch.
TEST_KULANZ_SEKUNDEN = 30


class UngueltigeAbgabe(Exception):
    """Die abgegebenen Antworten passen nicht zum Quiz oder Test (z. B. fremde Frage)."""


class TestZeitAbgelaufen(Exception):
    """Kein Testversuch läuft oder das Zeitlimit ist überschritten."""

    __test__ = False  # Kein pytest-Testfall, trotz des Namens.


@dataclass(frozen=True)
class FragenErgebnis:
    """Auswertung einer einzelnen Frage.

    Attributes:
        frage_id: ID der Frage.
        gewaehlte_antwort_id: ID der gewählten Antwort oder None, wenn unbeantwortet.
        richtige_antwort_id: ID der richtigen Antwort (None nur bei fehlerhaften Inhalten).
        ist_richtig: Ob die gewählte Antwort richtig ist.
        erklaerung: Kurze Begründung der richtigen Antwort.
    """

    frage_id: int
    gewaehlte_antwort_id: int | None
    richtige_antwort_id: int | None
    ist_richtig: bool
    erklaerung: str


@dataclass(frozen=True)
class QuizErgebnis:
    """Gesamtergebnis einer Quiz- oder Test-Abgabe.

    Attributes:
        punkte: Anzahl richtig beantworteter Fragen in dieser Abgabe.
        max_punkte: Anzahl der Fragen.
        bestwert: Bestes bisher gespeichertes Ergebnis (inklusive dieser Abgabe).
        fragen: Auswertung je Frage in der Reihenfolge der Fragen.
    """

    punkte: int
    max_punkte: int
    bestwert: int
    fragen: list[FragenErgebnis]


def _richtige_antwort_id(frage: Frage) -> int | None:
    """Sucht die richtige Antwort einer Frage.

    Args:
        frage: Frage mit vorgeladenen Antworten.

    Returns:
        ID der richtigen Antwort oder None, wenn die Inhalte keine richtige Antwort enthalten.
    """
    for antwort in frage.antworten.all():
        if antwort.ist_richtig:
            return antwort.id
    logger.warning("Frage %s hat keine richtige Antwort.", frage.id)
    return None


def _werte_aus(
    ziel: Quiz | Test, nutzer: User, auswahl: Mapping[int, int], name: str
) -> QuizErgebnis:
    """Wertet Antworten zu einem Quiz oder Test aus und speichert den Bestwert.

    Unbeantwortete Fragen zählen als falsch.

    Args:
        ziel: Das Quiz oder der Test.
        nutzer: Der angemeldete Nutzer.
        auswahl: Zuordnung Frage-ID → gewählte Antwort-ID.
        name: „Quiz“ oder „Test“ für Fehlermeldungen.

    Returns:
        Das Ergebnis mit Punkten, Bestwert und Auswertung je Frage.

    Raises:
        UngueltigeAbgabe: Wenn es keine Fragen gibt oder Fragen bzw. Antworten
            nicht dazu gehören.
    """
    fragen = list(ziel.fragen.prefetch_related("antworten"))
    if not fragen:
        raise UngueltigeAbgabe(f"Das {name} hat keine Fragen.")

    fremde_fragen = set(auswahl) - {frage.id for frage in fragen}
    if fremde_fragen:
        raise UngueltigeAbgabe(f"Fragen gehören nicht zu diesem {name}: {sorted(fremde_fragen)}")

    ergebnisse: list[FragenErgebnis] = []
    for frage in fragen:
        gewaehlt = auswahl.get(frage.id)
        if gewaehlt is not None and gewaehlt not in {a.id for a in frage.antworten.all()}:
            raise UngueltigeAbgabe(f"Antwort {gewaehlt} gehört nicht zu Frage {frage.id}.")
        richtig = _richtige_antwort_id(frage)
        ergebnisse.append(
            FragenErgebnis(
                frage_id=frage.id,
                gewaehlte_antwort_id=gewaehlt,
                richtige_antwort_id=richtig,
                ist_richtig=gewaehlt is not None and gewaehlt == richtig,
                erklaerung=frage.erklaerung,
            )
        )

    punkte = sum(1 for ergebnis in ergebnisse if ergebnis.ist_richtig)
    bestwert = _speichere_bestwert(ziel, nutzer, punkte, len(fragen))
    return QuizErgebnis(punkte=punkte, max_punkte=len(fragen), bestwert=bestwert, fragen=ergebnisse)


def werte_quiz_aus(quiz: Quiz, nutzer: User, auswahl: Mapping[int, int]) -> QuizErgebnis:
    """Wertet eine Quiz-Abgabe aus und speichert das beste Ergebnis als Fortschritt.

    Hat sich die Fragenzahl des Quiz geändert, ersetzt die neue Abgabe den alten Wert.

    Args:
        quiz: Das abgegebene Quiz.
        nutzer: Der angemeldete Nutzer.
        auswahl: Zuordnung Frage-ID → gewählte Antwort-ID.

    Returns:
        Das Ergebnis mit Punkten, Bestwert und Auswertung je Frage.

    Raises:
        UngueltigeAbgabe: Wenn das Quiz keine Fragen hat oder Fragen bzw. Antworten
            nicht zu diesem Quiz gehören.
    """
    return _werte_aus(quiz, nutzer, auswahl, "Quiz")


def _speichere_bestwert(ziel: Quiz | Test, nutzer: User, punkte: int, max_punkte: int) -> int:
    """Speichert das Ergebnis, wenn es besser ist oder sich die Fragenzahl geändert hat.

    Args:
        ziel: Das Quiz oder der Test.
        nutzer: Der Nutzer.
        punkte: Erreichte Punkte dieser Abgabe.
        max_punkte: Maximal erreichbare Punkte.

    Returns:
        Den gespeicherten Bestwert nach dieser Abgabe.
    """
    feld = "quiz" if isinstance(ziel, Quiz) else "test"
    with transaction.atomic():
        fortschritt, neu = Fortschritt.objects.select_for_update().get_or_create(
            nutzer=nutzer, **{feld: ziel}, defaults={"punkte": punkte, "max_punkte": max_punkte}
        )
        alter_wert = fortschritt.punkte or 0
        if not neu and (fortschritt.max_punkte != max_punkte or punkte > alter_wert):
            fortschritt.punkte = punkte
            fortschritt.max_punkte = max_punkte
            fortschritt.save(update_fields=["punkte", "max_punkte", "erledigt_am"])
    return fortschritt.punkte if fortschritt.punkte is not None else punkte


def markiere_abschnitt_gelesen(abschnitt: Abschnitt, nutzer: User) -> Fortschritt:
    """Markiert einen Abschnitt für den Nutzer als gelesen (mehrfacher Aufruf ist harmlos).

    Args:
        abschnitt: Der gelesene Abschnitt.
        nutzer: Der Nutzer.

    Returns:
        Den Fortschritts-Eintrag des Abschnitts.
    """
    fortschritt, _ = Fortschritt.objects.get_or_create(nutzer=nutzer, abschnitt=abschnitt)
    return fortschritt


# --- Tests mit Zeitlimit --------------------------------------------------------


@dataclass(frozen=True)
class TestStart:
    """Ein laufender Testversuch mit Restzeit.

    Attributes:
        versuch_id: ID des Versuchs.
        gestartet_am: Startzeit auf dem Server.
        endet_am: Ende des Zeitlimits.
        sekunden_rest: Restzeit in Sekunden (nie negativ). Die Oberfläche zählt von
            diesem Wert herunter, damit die Uhr des Geräts keine Rolle spielt.
    """

    __test__ = False  # Kein pytest-Testfall, trotz des Namens.

    versuch_id: int
    gestartet_am: datetime
    endet_am: datetime
    sekunden_rest: int


def _ende(versuch: TestVersuch) -> datetime:
    """Berechnet das Ende des Zeitlimits eines Versuchs.

    Args:
        versuch: Der Versuch.

    Returns:
        Startzeit plus Zeitlimit des Tests.
    """
    return versuch.gestartet_am + timedelta(minutes=versuch.test.zeitlimit_minuten)


def _laufender_versuch(test: Test, nutzer: User) -> TestVersuch | None:
    """Sucht (und sperrt) den laufenden Versuch eines Nutzers.

    Args:
        test: Der Test.
        nutzer: Der Nutzer.

    Returns:
        Den laufenden Versuch oder None. Aufruf nur innerhalb einer Transaktion.
    """
    return (
        TestVersuch.objects.select_for_update()
        .select_related("test")
        .filter(nutzer=nutzer, test=test, abgegeben_am__isnull=True)
        .first()
    )


def _ist_zu_spaet(versuch: TestVersuch, jetzt: datetime) -> bool:
    """Prüft, ob das Zeitlimit samt Kulanz überschritten ist.

    Args:
        versuch: Der Versuch.
        jetzt: Aktuelle Zeit.

    Returns:
        True, wenn eine Abgabe nicht mehr zählt.
    """
    return jetzt > _ende(versuch) + timedelta(seconds=TEST_KULANZ_SEKUNDEN)


def starte_test(test: Test, nutzer: User) -> TestStart:
    """Startet einen Testversuch oder setzt den laufenden fort.

    Ein abgelaufener, nie abgegebener Versuch wird beendet (ohne Ergebnis) und
    durch einen neuen ersetzt.

    Args:
        test: Der Test.
        nutzer: Der angemeldete Nutzer.

    Returns:
        Den laufenden Versuch mit Restzeit.
    """
    jetzt = timezone.now()
    with transaction.atomic():
        versuch = _laufender_versuch(test, nutzer)
        if versuch is not None and _ist_zu_spaet(versuch, jetzt):
            versuch.abgegeben_am = jetzt
            versuch.save(update_fields=["abgegeben_am"])
            versuch = None
        if versuch is None:
            try:
                with transaction.atomic():
                    versuch = TestVersuch.objects.create(nutzer=nutzer, test=test)
            except IntegrityError:
                # Paralleler Start (z. B. Doppelklick): den bereits laufenden Versuch nehmen.
                logger.info("Paralleler Teststart: Nutzer %s, Test %s.", nutzer.pk, test.pk)
                versuch = TestVersuch.objects.select_related("test").get(
                    nutzer=nutzer, test=test, abgegeben_am__isnull=True
                )
    endet = _ende(versuch)
    rest = max(0, int((endet - jetzt).total_seconds()))
    return TestStart(versuch.id, versuch.gestartet_am, endet, rest)


def werte_test_aus(test: Test, nutzer: User, auswahl: Mapping[int, int]) -> QuizErgebnis:
    """Wertet die Abgabe eines laufenden Testversuchs aus.

    Die Abgabe zählt, wenn sie spätestens `TEST_KULANZ_SEKUNDEN` nach Ablauf des
    Zeitlimits eintrifft. Danach ist der Versuch beendet und nichts wird gespeichert.
    Die Lösungen erfährt der Nutzer erst mit dieser Auswertung; jeder weitere Versuch
    braucht einen neuen Start. Eine ungültige Abgabe beendet den Versuch nicht.

    Args:
        test: Der Test.
        nutzer: Der angemeldete Nutzer.
        auswahl: Zuordnung Frage-ID → gewählte Antwort-ID.

    Returns:
        Das Ergebnis mit Punkten, Bestwert und Auswertung je Frage.

    Raises:
        TestZeitAbgelaufen: Wenn kein Versuch läuft oder das Zeitlimit überschritten ist.
        UngueltigeAbgabe: Wenn Fragen oder Antworten nicht zum Test gehören.
    """
    jetzt = timezone.now()
    with transaction.atomic():
        versuch = _laufender_versuch(test, nutzer)
        if versuch is None:
            raise TestZeitAbgelaufen("Es läuft kein Testversuch. Starte den Test zuerst.")
        zu_spaet = _ist_zu_spaet(versuch, jetzt)
        # Bei zu später Abgabe wird der Versuch beendet; die Ausnahme folgt erst nach
        # der Transaktion, sonst würde das Beenden zurückgerollt.
        ergebnis = None if zu_spaet else _werte_aus(test, nutzer, auswahl, "Test")
        versuch.abgegeben_am = jetzt
        versuch.save(update_fields=["abgegeben_am"])
    if ergebnis is None:
        raise TestZeitAbgelaufen("Das Zeitlimit ist abgelaufen.")
    return ergebnis


# --- Projektaufgaben ------------------------------------------------------------


@dataclass(frozen=True)
class ProjektStand:
    """Stand einer Projektaufgabe für einen Nutzer.

    Attributes:
        erledigt_ids: IDs der abgehakten Checklisten-Punkte.
        erledigt: Anzahl abgehakter Punkte.
        gesamt: Anzahl der Punkte der Checkliste.
        abgeschlossen: Ob die Checkliste vollständig abgehakt ist.
    """

    erledigt_ids: frozenset[int]
    erledigt: int
    gesamt: int
    abgeschlossen: bool


def projekt_stand(projekt: Projektaufgabe, nutzer: User) -> ProjektStand:
    """Ermittelt, welche Checklisten-Punkte der Nutzer abgehakt hat.

    Args:
        projekt: Die Projektaufgabe.
        nutzer: Der angemeldete Nutzer.

    Returns:
        Den Stand mit Zählung.
    """
    gesamt = projekt.punkte.count()
    erledigt_ids = frozenset(
        ProjektPunktErledigt.objects.filter(
            nutzer=nutzer, punkt__projektaufgabe=projekt
        ).values_list("punkt_id", flat=True)
    )
    return ProjektStand(
        erledigt_ids=erledigt_ids,
        erledigt=len(erledigt_ids),
        gesamt=gesamt,
        abgeschlossen=gesamt > 0 and len(erledigt_ids) == gesamt,
    )


def setze_projektpunkt(punkt: ProjektPunkt, nutzer: User, erledigt: bool) -> ProjektStand:
    """Hakt einen Checklisten-Punkt ab oder nimmt den Haken zurück.

    Ist danach die ganze Checkliste abgehakt, gilt das Projekt als erledigt
    (Fortschritt mit erledigten und gesamten Punkten). Nimmt der Nutzer später einen
    Haken zurück, entfällt dieser Fortschritt wieder.

    Args:
        punkt: Der Checklisten-Punkt.
        nutzer: Der angemeldete Nutzer.
        erledigt: Ob der Punkt abgehakt sein soll.

    Returns:
        Den neuen Stand der Projektaufgabe.
    """
    projekt = punkt.projektaufgabe
    with transaction.atomic():
        if erledigt:
            ProjektPunktErledigt.objects.get_or_create(nutzer=nutzer, punkt=punkt)
        else:
            ProjektPunktErledigt.objects.filter(nutzer=nutzer, punkt=punkt).delete()
        stand = projekt_stand(projekt, nutzer)
        if stand.abgeschlossen:
            Fortschritt.objects.update_or_create(
                nutzer=nutzer,
                projektaufgabe=projekt,
                defaults={"punkte": stand.erledigt, "max_punkte": stand.gesamt},
            )
        else:
            Fortschritt.objects.filter(nutzer=nutzer, projektaufgabe=projekt).delete()
    return stand
