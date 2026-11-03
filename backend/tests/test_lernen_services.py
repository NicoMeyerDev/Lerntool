"""Tests für die Geschäftslogik der Lern-App (ohne HTTP)."""

import pytest
from django.contrib.auth.models import User

from lernen import models as m
from lernen.services import UngueltigeAbgabe, werte_quiz_aus
from tests.fabrik import Inhalte, baue_frage

pytestmark = pytest.mark.django_db


def test_geaendertes_quiz_ersetzt_alten_bestwert(inhalte: Inhalte, nutzer: User) -> None:
    """Kommt eine Frage dazu, ersetzt die neue Abgabe den alten Wert (anderes Maximum)."""
    frage1, antworten1 = baue_frage(inhalte.quiz, 1)
    werte_quiz_aus(inhalte.quiz, nutzer, {frage1.pk: antworten1[0].pk})
    baue_frage(inhalte.quiz, 2)

    ergebnis = werte_quiz_aus(inhalte.quiz, nutzer, {})

    fortschritt = m.Fortschritt.objects.get(nutzer=nutzer, quiz=inhalte.quiz)
    assert (fortschritt.punkte, fortschritt.max_punkte) == (0, 2)
    assert ergebnis.bestwert == 0


def test_frage_ohne_richtige_antwort_zaehlt_als_falsch(
    inhalte: Inhalte, nutzer: User, caplog: pytest.LogCaptureFixture
) -> None:
    """Fehlerhafte Inhalte führen nicht zum Absturz, sondern zu „falsch“ und einer Warnung."""
    frage, antworten = baue_frage(inhalte.quiz, 1, richtig_an_position=None)

    ergebnis = werte_quiz_aus(inhalte.quiz, nutzer, {frage.pk: antworten[0].pk})

    assert ergebnis.punkte == 0
    assert ergebnis.fragen[0].richtige_antwort_id is None
    assert "keine richtige Antwort" in caplog.text


def test_fremde_frage_loest_fehler_aus(inhalte: Inhalte, nutzer: User) -> None:
    """Eine Frage-ID, die nicht zum Quiz gehört, wird abgelehnt."""
    baue_frage(inhalte.quiz, 1)

    with pytest.raises(UngueltigeAbgabe, match="gehören nicht zu diesem Quiz"):
        werte_quiz_aus(inhalte.quiz, nutzer, {999_999: 1})


def test_fremde_antwort_loest_fehler_aus(inhalte: Inhalte, nutzer: User) -> None:
    """Eine Antwort, die zu einer anderen Frage gehört, wird mit klarer Meldung abgelehnt."""
    frage1, _ = baue_frage(inhalte.quiz, 1)
    _, antworten2 = baue_frage(inhalte.quiz, 2)

    with pytest.raises(UngueltigeAbgabe, match=f"gehört nicht zu Frage {frage1.pk}"):
        werte_quiz_aus(inhalte.quiz, nutzer, {frage1.pk: antworten2[0].pk})

    assert not m.Fortschritt.objects.exists()


def test_gleichstand_aendert_gespeicherten_eintrag_nicht(inhalte: Inhalte, nutzer: User) -> None:
    """Bei gleichem Ergebnis bleibt der Eintrag unverändert (auch der Zeitpunkt)."""
    frage, antworten = baue_frage(inhalte.quiz, 1)
    werte_quiz_aus(inhalte.quiz, nutzer, {frage.pk: antworten[0].pk})
    vorher = m.Fortschritt.objects.get(nutzer=nutzer, quiz=inhalte.quiz).erledigt_am

    ergebnis = werte_quiz_aus(inhalte.quiz, nutzer, {frage.pk: antworten[0].pk})

    nachher = m.Fortschritt.objects.get(nutzer=nutzer, quiz=inhalte.quiz)
    assert ergebnis.bestwert == 1
    assert (nachher.punkte, nachher.erledigt_am) == (1, vorher)
