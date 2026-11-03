"""Tests für das Datenmodell der Lern-App (Beziehungen, Sortierung, Datenbank-Regeln).

Die Modelle werden als Modul `m` importiert, damit pytest das Modell `Test`
nicht für eine Testklasse hält.
"""

from dataclasses import dataclass

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from lernen import models as m

pytestmark = pytest.mark.django_db


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


@pytest.fixture
def inhalte() -> Inhalte:
    """Legt Thema, Phase, Lektion, Abschnitt, Quiz, Test und Projektaufgabe an."""
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


@pytest.fixture
def nutzer() -> User:
    """Legt einen Nutzer an."""
    return User.objects.create_user(username="lernender", password="geheim-123")


# --- Aufbau und Beziehungen -------------------------------------------------


def test_inhaltskette_ist_ueber_related_names_erreichbar(inhalte: Inhalte) -> None:
    """Von Thema bis Quiz und Test ist alles über die Rückwärts-Beziehungen erreichbar."""
    assert list(inhalte.thema.phasen.all()) == [inhalte.phase]
    assert list(inhalte.phase.lektionen.all()) == [inhalte.lektion]
    assert list(inhalte.phase.projektaufgaben.all()) == [inhalte.projekt]
    assert list(inhalte.lektion.abschnitte.all()) == [inhalte.abschnitt]
    assert inhalte.abschnitt.quiz == inhalte.quiz
    assert inhalte.lektion.test == inhalte.test


def test_str_liefert_lesbare_namen(inhalte: Inhalte) -> None:
    """Die Textdarstellung zeigt Titel bzw. Zuordnung."""
    assert str(inhalte.thema) == "PHP/Laravel"
    assert str(inhalte.quiz) == "Quiz: Was ist ein Array?"
    assert str(inhalte.test) == "Test: Arrays"


def test_lektionen_sind_nach_reihenfolge_sortiert(inhalte: Inhalte) -> None:
    """Lektionen kommen in der festgelegten Reihenfolge, nicht in Anlage-Reihenfolge."""
    m.Lektion.objects.create(phase=inhalte.phase, titel="Variablen", slug="var", reihenfolge=0)

    titel = [lektion.titel for lektion in inhalte.phase.lektionen.all()]

    assert titel == ["Variablen", "Arrays"]


def test_loeschen_eines_themas_entfernt_alle_inhalte(inhalte: Inhalte) -> None:
    """Wird ein Thema gelöscht, verschwinden auch alle untergeordneten Inhalte."""
    inhalte.thema.delete()

    assert m.Phase.objects.count() == 0
    assert m.Abschnitt.objects.count() == 0
    assert m.Quiz.objects.count() == 0
    assert m.Test.objects.count() == 0
    assert m.Projektaufgabe.objects.count() == 0


# --- Eindeutigkeit ------------------------------------------------------------


def test_reihenfolge_ist_je_phase_eindeutig(inhalte: Inhalte) -> None:
    """Zwei Lektionen derselben Phase dürfen nicht dieselbe Position haben."""
    with pytest.raises(IntegrityError), transaction.atomic():
        m.Lektion.objects.create(phase=inhalte.phase, titel="X", slug="x", reihenfolge=1)


def test_gleiche_reihenfolge_in_anderer_phase_ist_erlaubt(inhalte: Inhalte) -> None:
    """Position 1 darf es in jeder Phase einmal geben."""
    andere = m.Phase.objects.create(thema=inhalte.thema, titel="Laravel", slug="lv", reihenfolge=2)

    lektion = m.Lektion.objects.create(phase=andere, titel="Routing", slug="r", reihenfolge=1)

    assert lektion.pk is not None


def test_quelle_ist_je_lektion_eindeutig(inhalte: Inhalte) -> None:
    """Derselbe Link darf pro Lektion nur einmal als Quelle stehen."""
    url = "https://www.php.net/manual/de/language.types.array.php"
    m.Quelle.objects.create(lektion=inhalte.lektion, titel="PHP-Handbuch: Arrays", url=url)

    with pytest.raises(IntegrityError), transaction.atomic():
        m.Quelle.objects.create(lektion=inhalte.lektion, titel="Doppelt", url=url)


def test_zweites_quiz_fuer_denselben_abschnitt_ist_verboten(inhalte: Inhalte) -> None:
    """Jeder Abschnitt hat höchstens ein Quiz."""
    with pytest.raises(IntegrityError), transaction.atomic():
        m.Quiz.objects.create(abschnitt=inhalte.abschnitt)


# --- Fragen und Antworten -----------------------------------------------------


def test_frage_kann_zu_quiz_oder_test_gehoeren(inhalte: Inhalte) -> None:
    """Eine Frage gehört entweder zu einem Quiz oder zu einem Test."""
    m.Frage.objects.create(quiz=inhalte.quiz, text="Quizfrage", reihenfolge=1)
    m.Frage.objects.create(test=inhalte.test, text="Testfrage", reihenfolge=1)

    assert inhalte.quiz.fragen.count() == 1
    assert inhalte.test.fragen.count() == 1


def test_frage_ohne_quiz_und_test_ist_verboten() -> None:
    """Eine Frage ohne Zuordnung verletzt die Datenbank-Regel."""
    with pytest.raises(IntegrityError), transaction.atomic():
        m.Frage.objects.create(text="Verwaist", reihenfolge=1)


def test_frage_mit_quiz_und_test_ist_verboten(inhalte: Inhalte) -> None:
    """Eine Frage darf nicht gleichzeitig zu Quiz und Test gehören."""
    with pytest.raises(IntegrityError), transaction.atomic():
        m.Frage.objects.create(quiz=inhalte.quiz, test=inhalte.test, text="Beides", reihenfolge=1)


def test_hoechstens_eine_richtige_antwort_je_frage(inhalte: Inhalte) -> None:
    """Mehrere falsche Antworten sind erlaubt, aber nur eine richtige."""
    frage = m.Frage.objects.create(quiz=inhalte.quiz, text="2 + 2?", reihenfolge=1)
    m.Antwort.objects.create(frage=frage, text="4", ist_richtig=True, reihenfolge=1)
    m.Antwort.objects.create(frage=frage, text="3", reihenfolge=2)
    m.Antwort.objects.create(frage=frage, text="5", reihenfolge=3)

    with pytest.raises(IntegrityError), transaction.atomic():
        m.Antwort.objects.create(frage=frage, text="vier", ist_richtig=True, reihenfolge=4)

    assert list(frage.antworten.values_list("text", flat=True)) == ["4", "3", "5"]


# --- Test-Zeitlimit -----------------------------------------------------------


def test_test_hat_standardmaessig_30_minuten(inhalte: Inhalte) -> None:
    """Ohne Angabe beträgt das Zeitlimit 30 Minuten."""
    assert inhalte.test.zeitlimit_minuten == 30


@pytest.mark.parametrize("minuten", [0, 31])
def test_zeitlimit_ausserhalb_1_bis_30_ist_verboten(inhalte: Inhalte, minuten: int) -> None:
    """Datenbank und Validierung lehnen Zeitlimits unter 1 oder über 30 Minuten ab."""
    inhalte.test.zeitlimit_minuten = minuten

    with pytest.raises(ValidationError):
        inhalte.test.full_clean()
    with pytest.raises(IntegrityError), transaction.atomic():
        inhalte.test.save()


# --- Fortschritt --------------------------------------------------------------


def test_fortschritt_fuer_jedes_ziel_speicherbar(inhalte: Inhalte, nutzer: User) -> None:
    """Abschnitt, Quiz (mit Punkten), Test und Projekt lassen sich als erledigt speichern."""
    m.Fortschritt.objects.create(nutzer=nutzer, abschnitt=inhalte.abschnitt)
    m.Fortschritt.objects.create(nutzer=nutzer, quiz=inhalte.quiz, punkte=3, max_punkte=4)
    m.Fortschritt.objects.create(nutzer=nutzer, test=inhalte.test, punkte=10, max_punkte=10)
    m.Fortschritt.objects.create(nutzer=nutzer, projektaufgabe=inhalte.projekt)

    assert m.Fortschritt.objects.filter(nutzer=nutzer).count() == 4


def test_fortschritt_ohne_ziel_ist_verboten(nutzer: User) -> None:
    """Ein Fortschritt muss sich auf genau ein Ziel beziehen."""
    with pytest.raises(IntegrityError), transaction.atomic():
        m.Fortschritt.objects.create(nutzer=nutzer)


def test_fortschritt_mit_zwei_zielen_ist_verboten(inhalte: Inhalte, nutzer: User) -> None:
    """Ein Fortschritt darf nicht gleichzeitig zwei Ziele haben."""
    with pytest.raises(IntegrityError), transaction.atomic():
        m.Fortschritt.objects.create(nutzer=nutzer, abschnitt=inhalte.abschnitt, quiz=inhalte.quiz)


def test_fortschritt_je_nutzer_und_ziel_nur_einmal(inhalte: Inhalte, nutzer: User) -> None:
    """Pro Nutzer und Ziel gibt es nur einen Eintrag (wird später aktualisiert)."""
    m.Fortschritt.objects.create(nutzer=nutzer, quiz=inhalte.quiz, punkte=1, max_punkte=4)

    with pytest.raises(IntegrityError), transaction.atomic():
        m.Fortschritt.objects.create(nutzer=nutzer, quiz=inhalte.quiz, punkte=4, max_punkte=4)


def test_anderer_nutzer_hat_eigenen_fortschritt(inhalte: Inhalte, nutzer: User) -> None:
    """Derselbe Abschnitt kann für verschiedene Nutzer erledigt sein."""
    zweiter = User.objects.create_user(username="zweiter", password="geheim-456")
    m.Fortschritt.objects.create(nutzer=nutzer, abschnitt=inhalte.abschnitt)
    m.Fortschritt.objects.create(nutzer=zweiter, abschnitt=inhalte.abschnitt)

    assert inhalte.abschnitt.fortschritte.count() == 2


@pytest.mark.parametrize(
    ("punkte", "max_punkte"),
    [(5, 4), (3, None), (None, 4), (0, 0)],
)
def test_ungueltige_punkte_sind_verboten(
    inhalte: Inhalte, nutzer: User, punkte: int | None, max_punkte: int | None
) -> None:
    """Punkte nur zusammen mit Maximum, Maximum > 0 und Punkte nicht über dem Maximum."""
    with pytest.raises(IntegrityError), transaction.atomic():
        m.Fortschritt.objects.create(
            nutzer=nutzer, quiz=inhalte.quiz, punkte=punkte, max_punkte=max_punkte
        )


# --- Ergänzungen: weitere Eindeutigkeiten -------------------------------------


def test_zweiter_test_fuer_dieselbe_lektion_ist_verboten(inhalte: Inhalte) -> None:
    """Jede Lektion hat höchstens einen Test."""
    with pytest.raises(IntegrityError), transaction.atomic():
        m.Test.objects.create(lektion=inhalte.lektion)


@pytest.mark.parametrize(
    "doppelt",
    [
        {"titel": "Englisch", "slug": "php-laravel", "reihenfolge": 2},
        {"titel": "Englisch", "slug": "englisch", "reihenfolge": 1},
    ],
)
def test_thema_slug_und_reihenfolge_sind_eindeutig(
    inhalte: Inhalte, doppelt: dict[str, str | int]
) -> None:
    """Slug und Position eines Themas gibt es nur einmal."""
    with pytest.raises(IntegrityError), transaction.atomic():
        m.Thema.objects.create(**doppelt)


@pytest.mark.parametrize(
    ("slug", "reihenfolge"),
    [("php-basics", 2), ("anders", 1)],
)
def test_phase_slug_und_reihenfolge_je_thema_eindeutig(
    inhalte: Inhalte, slug: str, reihenfolge: int
) -> None:
    """Innerhalb eines Themas sind Slug und Position einer Phase eindeutig."""
    with pytest.raises(IntegrityError), transaction.atomic():
        m.Phase.objects.create(thema=inhalte.thema, titel="X", slug=slug, reihenfolge=reihenfolge)


def test_lektion_slug_je_phase_eindeutig(inhalte: Inhalte) -> None:
    """Innerhalb einer Phase gibt es jeden Lektions-Slug nur einmal."""
    with pytest.raises(IntegrityError), transaction.atomic():
        m.Lektion.objects.create(phase=inhalte.phase, titel="X", slug="arrays", reihenfolge=2)


def test_frage_reihenfolge_je_quiz_und_test(inhalte: Inhalte) -> None:
    """Position 1 darf es im Quiz und im Test je einmal geben, aber nicht doppelt im Quiz."""
    m.Frage.objects.create(quiz=inhalte.quiz, text="Q1", reihenfolge=1)
    m.Frage.objects.create(test=inhalte.test, text="T1", reihenfolge=1)

    with pytest.raises(IntegrityError), transaction.atomic():
        m.Frage.objects.create(quiz=inhalte.quiz, text="Q1 doppelt", reihenfolge=1)
    with pytest.raises(IntegrityError), transaction.atomic():
        m.Frage.objects.create(test=inhalte.test, text="T1 doppelt", reihenfolge=1)


def test_antwort_reihenfolge_je_frage_eindeutig(inhalte: Inhalte) -> None:
    """Zwei Antworten derselben Frage dürfen nicht dieselbe Position haben."""
    frage = m.Frage.objects.create(quiz=inhalte.quiz, text="F", reihenfolge=1)
    m.Antwort.objects.create(frage=frage, text="A", reihenfolge=1)

    with pytest.raises(IntegrityError), transaction.atomic():
        m.Antwort.objects.create(frage=frage, text="B", reihenfolge=1)


# --- Ergänzungen: Validierung, Grenzfälle, Löschen ---------------------------


def test_quelle_braucht_gueltigen_link(inhalte: Inhalte) -> None:
    """Eine Quelle ohne gültige URL wird bei der Validierung abgelehnt."""
    quelle = m.Quelle(lektion=inhalte.lektion, titel="Ohne Link", url="kein-link")

    with pytest.raises(ValidationError):
        quelle.full_clean()


def test_null_punkte_sind_ein_gueltiges_ergebnis(inhalte: Inhalte, nutzer: User) -> None:
    """0 von 4 Punkten ist erlaubt (Grenzfall der Punkte-Regel)."""
    fortschritt = m.Fortschritt.objects.create(
        nutzer=nutzer, quiz=inhalte.quiz, punkte=0, max_punkte=4
    )

    assert fortschritt.pk is not None


def test_loeschen_entfernt_abhaengige_daten(inhalte: Inhalte, nutzer: User) -> None:
    """Löschen eines Themas entfernt auch Fragen, Antworten, Quellen und Fortschritt."""
    frage = m.Frage.objects.create(quiz=inhalte.quiz, text="F", reihenfolge=1)
    m.Antwort.objects.create(frage=frage, text="A", ist_richtig=True, reihenfolge=1)
    m.Quelle.objects.create(lektion=inhalte.lektion, titel="Q", url="https://www.php.net/")
    m.Fortschritt.objects.create(nutzer=nutzer, abschnitt=inhalte.abschnitt)

    inhalte.thema.delete()

    assert m.Frage.objects.count() == 0
    assert m.Antwort.objects.count() == 0
    assert m.Quelle.objects.count() == 0
    assert m.Fortschritt.objects.count() == 0


def test_loeschen_eines_nutzers_entfernt_seinen_fortschritt(inhalte: Inhalte, nutzer: User) -> None:
    """Der Fortschritt gehört zum Nutzer und verschwindet mit ihm; Inhalte bleiben."""
    m.Fortschritt.objects.create(nutzer=nutzer, abschnitt=inhalte.abschnitt)

    nutzer.delete()

    assert m.Fortschritt.objects.count() == 0
    assert m.Abschnitt.objects.count() == 1


def test_str_von_quelle_frage_antwort_fortschritt(inhalte: Inhalte, nutzer: User) -> None:
    """Auch die übrigen Modelle haben eine lesbare Textdarstellung."""
    quelle = m.Quelle.objects.create(
        lektion=inhalte.lektion, titel="PHP-Handbuch", url="https://www.php.net/"
    )
    frage = m.Frage.objects.create(quiz=inhalte.quiz, text="x" * 80, reihenfolge=1)
    antwort = m.Antwort.objects.create(frage=frage, text="Ja", reihenfolge=1)
    fortschritt = m.Fortschritt.objects.create(nutzer=nutzer, test=inhalte.test)

    assert str(quelle) == "PHP-Handbuch (https://www.php.net/)"
    assert str(frage) == "x" * 60
    assert str(antwort) == "Ja"
    assert str(fortschritt) == "lernender: Test: Arrays"
