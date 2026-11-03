"""Testdaten-Fabrik: baut kleine, vollständige Inhalte für Modell- und API-Tests."""

from dataclasses import dataclass

from lernen import models as m


@dataclass
class Inhalte:
    """Eine vollständige, minimale Inhaltskette für die Tests."""

    thema: m.Thema
    phase: m.Phase
    lektion: m.Lektion
    abschnitt: m.Abschnitt
    quiz: m.Quiz
    test: m.Test
    projekt: m.Projektaufgabe


def baue_inhalte() -> Inhalte:
    """Legt Thema, Phase, Lektion, Abschnitt, Quiz, Test und Projektaufgabe an.

    Returns:
        Die angelegten Objekte.
    """
    thema = m.Thema.objects.create(titel="PHP/Laravel", slug="php-laravel", reihenfolge=1)
    phase = m.Phase.objects.create(
        thema=thema, titel="PHP-Basics", slug="php-basics", reihenfolge=1
    )
    lektion = m.Lektion.objects.create(phase=phase, titel="Arrays", slug="arrays", reihenfolge=1)
    abschnitt = m.Abschnitt.objects.create(
        lektion=lektion, titel="Was ist ein Array?", inhalt="Text", reihenfolge=1
    )
    quiz = m.Quiz.objects.create(abschnitt=abschnitt)
    test = m.Test.objects.create(lektion=lektion)
    projekt = m.Projektaufgabe.objects.create(
        phase=phase, titel="Einkaufsliste", beschreibung="Aufgabe", reihenfolge=1
    )
    return Inhalte(thema, phase, lektion, abschnitt, quiz, test, projekt)


def baue_frage(
    quiz: m.Quiz | m.Test, reihenfolge: int, richtig_an_position: int | None = 1
) -> tuple[m.Frage, list[m.Antwort]]:
    """Legt eine Frage mit drei Antworten an.

    Args:
        quiz: Das Quiz oder der Test, zu dem die Frage gehört.
        reihenfolge: Position der Frage.
        richtig_an_position: Position (1–3) der richtigen Antwort oder None für
            eine fehlerhafte Frage ohne richtige Antwort.

    Returns:
        Die Frage und ihre Antworten in Reihenfolge.
    """
    zuordnung = {"test": quiz} if isinstance(quiz, m.Test) else {"quiz": quiz}
    frage = m.Frage.objects.create(
        **zuordnung,
        text=f"Frage {reihenfolge}",
        erklaerung="Weil es so ist.",
        reihenfolge=reihenfolge,
    )
    antworten = [
        m.Antwort.objects.create(
            frage=frage,
            text=f"Antwort {position}",
            ist_richtig=position == richtig_an_position,
            reihenfolge=position,
        )
        for position in (1, 2, 3)
    ]
    return frage, antworten
