"""Geschäftslogik der Lern-App: Quiz auswerten und Fortschritt speichern."""

import logging
from collections.abc import Mapping
from dataclasses import dataclass

from django.contrib.auth.models import User
from django.db import transaction

from lernen.models import Abschnitt, Fortschritt, Frage, Quiz

logger = logging.getLogger(__name__)


class UngueltigeAbgabe(Exception):
    """Die abgegebenen Antworten passen nicht zum Quiz (z. B. fremde Frage oder Antwort)."""


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
    """Gesamtergebnis einer Quiz-Abgabe.

    Attributes:
        punkte: Anzahl richtig beantworteter Fragen in dieser Abgabe.
        max_punkte: Anzahl der Fragen im Quiz.
        bestwert: Bestes bisher gespeichertes Ergebnis (inklusive dieser Abgabe).
        fragen: Auswertung je Frage in der Reihenfolge des Quiz.
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


def werte_quiz_aus(quiz: Quiz, nutzer: User, auswahl: Mapping[int, int]) -> QuizErgebnis:
    """Wertet eine Quiz-Abgabe aus und speichert das beste Ergebnis als Fortschritt.

    Unbeantwortete Fragen zählen als falsch. Gespeichert wird das beste Ergebnis;
    hat sich die Fragenzahl des Quiz geändert, ersetzt die neue Abgabe den alten Wert.

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
    fragen = list(quiz.fragen.prefetch_related("antworten"))
    if not fragen:
        raise UngueltigeAbgabe("Das Quiz hat keine Fragen.")

    fremde_fragen = set(auswahl) - {frage.id for frage in fragen}
    if fremde_fragen:
        raise UngueltigeAbgabe(f"Fragen gehören nicht zu diesem Quiz: {sorted(fremde_fragen)}")

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
    bestwert = _speichere_bestwert(quiz, nutzer, punkte, len(fragen))
    return QuizErgebnis(punkte=punkte, max_punkte=len(fragen), bestwert=bestwert, fragen=ergebnisse)


def _speichere_bestwert(quiz: Quiz, nutzer: User, punkte: int, max_punkte: int) -> int:
    """Speichert das Quiz-Ergebnis, wenn es besser ist oder sich das Quiz geändert hat.

    Args:
        quiz: Das Quiz.
        nutzer: Der Nutzer.
        punkte: Erreichte Punkte dieser Abgabe.
        max_punkte: Maximal erreichbare Punkte.

    Returns:
        Den gespeicherten Bestwert nach dieser Abgabe.
    """
    with transaction.atomic():
        fortschritt, neu = Fortschritt.objects.select_for_update().get_or_create(
            nutzer=nutzer, quiz=quiz, defaults={"punkte": punkte, "max_punkte": max_punkte}
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
