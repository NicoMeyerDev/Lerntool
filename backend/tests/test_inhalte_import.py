"""Tests für den Import der Lerninhalte aus YAML-Dateien (C2).

Modelle werden als Modul `m` importiert, damit pytest das Modell `Test` nicht sammelt.
"""

from io import StringIO
from pathlib import Path
from typing import Any

import pytest
import yaml
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError

from lernen import models as m
from lernen.inhalte_import import InhaltsFehler, importiere_inhalte

pytestmark = pytest.mark.django_db


def frage(text: str = "Was ist 1+1?", richtig: int = 0, anzahl: int = 3) -> dict[str, Any]:
    """Baut eine gültige Frage.

    Args:
        text: Fragetext.
        richtig: Index der richtigen Antwort.
        anzahl: Anzahl der Antworten.

    Returns:
        Die Frage als Dictionary für die YAML-Datei.
    """
    return {
        "frage": text,
        "erklaerung": "Weil es so ist.",
        "antworten": [{"text": f"A{i}", "richtig": i == richtig} for i in range(anzahl)],
    }


def lektion_daten() -> dict[str, Any]:
    """Baut eine gültige Lektion mit zwei Abschnitten.

    Returns:
        Die Lektion als Dictionary für die YAML-Datei.
    """
    return {
        "titel": "Variablen",
        "zusammenfassung": "Kurz.",
        "quellen": [{"titel": "PHP-Handbuch", "url": "https://www.php.net/manual/en/"}],
        "abschnitte": [
            {"titel": "Erster", "inhalt": "Text 1", "quiz": [frage()]},
            {"titel": "Zweiter", "inhalt": "Text 2", "quiz": [frage(), frage("Frage 2")]},
        ],
        "test": {"zeitlimit_minuten": 20, "fragen": [frage()]},
    }


def schreibe(wurzel: Path, lektion: dict[str, Any] | None = None) -> Path:
    """Schreibt einen kleinen, gültigen Inhaltsbaum.

    Args:
        wurzel: Zielordner.
        lektion: Optional abweichende Lektionsdaten.

    Returns:
        Den Ordner mit dem Thema.
    """
    thema = wurzel / "php-laravel"
    phase = thema / "01-php-basics"
    phase.mkdir(parents=True)
    (thema / "thema.yaml").write_text(
        yaml.safe_dump({"titel": "PHP/Laravel", "reihenfolge": 1}), encoding="utf-8"
    )
    (phase / "phase.yaml").write_text(
        yaml.safe_dump(
            {
                "titel": "PHP-Basics",
                "projekt": {
                    "titel": "Trainingslog",
                    "beschreibung": "Aufgabe",
                    "punkte": ["a", "b"],
                },
            }
        ),
        encoding="utf-8",
    )
    (phase / "01-variablen.yaml").write_text(
        yaml.safe_dump(lektion or lektion_daten(), allow_unicode=True), encoding="utf-8"
    )
    return thema


def fehler_von(wurzel: Path) -> list[str]:
    """Führt den Import aus und gibt die Fehlermeldungen zurück.

    Args:
        wurzel: Inhaltsordner.

    Returns:
        Die Meldungen der `InhaltsFehler`-Ausnahme.
    """
    with pytest.raises(InhaltsFehler) as ausnahme:
        importiere_inhalte(wurzel)
    return ausnahme.value.meldungen


def test_import_legt_alles_an(tmp_path: Path) -> None:
    """Thema, Phase, Lektion, Quelle, Abschnitte, Quizze, Test und Projekt entstehen."""
    schreibe(tmp_path)

    bericht = importiere_inhalte(tmp_path)

    assert (bericht.phasen, bericht.lektionen, bericht.abschnitte) == (1, 1, 2)
    assert (bericht.fragen, bericht.projekte, bericht.warnungen) == (4, 1, [])
    lektion = m.Lektion.objects.get(slug="variablen")
    assert lektion.phase.thema.slug == "php-laravel"
    assert lektion.phase.reihenfolge == 1
    assert lektion.quellen.count() == 1
    assert lektion.abschnitte.count() == 2
    assert lektion.test.zeitlimit_minuten == 20
    assert m.Quiz.objects.get(abschnitt__reihenfolge=2).fragen.count() == 2
    assert m.Antwort.objects.filter(ist_richtig=True).count() == m.Frage.objects.count()
    assert m.ProjektPunkt.objects.count() == 2


def test_import_ist_wiederholbar_und_behaelt_fortschritt(tmp_path: Path, nutzer: User) -> None:
    """Ein zweiter Import dupliziert nichts und lässt Fortschritt bestehen."""
    schreibe(tmp_path)
    importiere_inhalte(tmp_path)
    abschnitt = m.Abschnitt.objects.get(reihenfolge=1)
    m.Fortschritt.objects.create(nutzer=nutzer, abschnitt=abschnitt)

    importiere_inhalte(tmp_path)

    assert m.Abschnitt.objects.count() == 2
    assert m.Frage.objects.count() == 4
    assert m.Fortschritt.objects.filter(abschnitt=abschnitt).count() == 1


def test_import_aktualisiert_geaenderten_text(tmp_path: Path) -> None:
    """Geänderte Texte und Fragen überschreiben die alten."""
    schreibe(tmp_path)
    importiere_inhalte(tmp_path)
    neu = lektion_daten()
    neu["abschnitte"][0]["inhalt"] = "Neuer Text"
    neu["abschnitte"][0]["quiz"] = [frage("Neue Frage?")]
    (tmp_path / "php-laravel" / "01-php-basics" / "01-variablen.yaml").write_text(
        yaml.safe_dump(neu, allow_unicode=True), encoding="utf-8"
    )

    importiere_inhalte(tmp_path)

    abschnitt = m.Abschnitt.objects.get(reihenfolge=1)
    assert abschnitt.inhalt == "Neuer Text"
    assert [f.text for f in abschnitt.quiz.fragen.all()] == ["Neue Frage?"]


def test_import_loescht_nichts_sondern_warnt(tmp_path: Path) -> None:
    """Abschnitte, die in der Datei fehlen, bleiben bestehen und lösen eine Warnung aus."""
    schreibe(tmp_path)
    importiere_inhalte(tmp_path)
    kurz = lektion_daten()
    kurz["abschnitte"] = kurz["abschnitte"][:1]
    (tmp_path / "php-laravel" / "01-php-basics" / "01-variablen.yaml").write_text(
        yaml.safe_dump(kurz, allow_unicode=True), encoding="utf-8"
    )

    bericht = importiere_inhalte(tmp_path)

    assert m.Abschnitt.objects.count() == 2
    assert any("Abschnitt" in w for w in bericht.warnungen)


def test_fehler_speichert_nichts(tmp_path: Path) -> None:
    """Bei Fehlern in einer Datei wird nichts gespeichert, auch nichts aus gültigen Dateien."""
    schreibe(tmp_path)
    kaputt = lektion_daten()
    kaputt["quellen"] = []
    (tmp_path / "php-laravel" / "01-php-basics" / "02-zweite.yaml").write_text(
        yaml.safe_dump(kaputt, allow_unicode=True), encoding="utf-8"
    )

    meldungen = fehler_von(tmp_path)

    assert any("quellen" in meldung for meldung in meldungen)
    assert m.Thema.objects.count() == 0


@pytest.mark.parametrize(
    ("aenderung", "erwartet"),
    [
        (lambda d: d.update(quellen=[]), "quellen"),
        (lambda d: d["quellen"][0].update(url="ftp://example.com/x"), "http(s)"),
        (lambda d: d["quellen"][0].update(url="kein link"), "http(s)"),
        (lambda d: d["quellen"].append(dict(d["quellen"][0])), "mehrfach"),
        (lambda d: d["abschnitte"][0].update(quiz=[]), "quiz"),
        (lambda d: d["abschnitte"][0].update(inhalt=""), "inhalt"),
        (
            lambda d: d["abschnitte"][0]["quiz"][0]["antworten"][1].update(richtig=True),
            "genau eine",
        ),
        (
            lambda d: d["abschnitte"][0]["quiz"][0]["antworten"][0].update(richtig=False),
            "genau eine",
        ),
        (
            lambda d: d["abschnitte"][0]["quiz"][0].update(
                antworten=[{"text": "x", "richtig": True}]
            ),
            "mindestens zwei",
        ),
        (lambda d: d["test"].update(zeitlimit_minuten=31), "zeitlimit_minuten"),
        (lambda d: d["test"].update(zeitlimit_minuten=0), "zeitlimit_minuten"),
        (lambda d: d["test"].update(fragen=[]), "fragen"),
        (lambda d: d.pop("test"), "test"),
        (lambda d: d.pop("titel"), "titel"),
    ],
)
def test_ungueltige_lektion_wird_abgelehnt(tmp_path: Path, aenderung: Any, erwartet: str) -> None:
    """Jede verletzte Regel führt zu einer Fehlermeldung mit Fundstelle."""
    daten = lektion_daten()
    aenderung(daten)
    schreibe(tmp_path, daten)

    meldungen = fehler_von(tmp_path)

    assert any(erwartet in meldung for meldung in meldungen), meldungen
    assert all("01-variablen.yaml" in meldung for meldung in meldungen)


def test_falsche_namen_und_fehlende_dateien(tmp_path: Path) -> None:
    """Ordner ohne Nummer und Phasen ohne phase.yaml werden gemeldet."""
    thema = schreibe(tmp_path)
    (thema / "Ohne-Nummer").mkdir()
    (thema / "02-leer").mkdir()

    meldungen = fehler_von(tmp_path)

    assert any("Ohne-Nummer" in m_ and "01-kurzname" in m_ for m_ in meldungen)
    assert any("phase.yaml fehlt" in m_ for m_ in meldungen)


def test_fehlender_ordner_und_thema_yaml(tmp_path: Path) -> None:
    """Ein nicht vorhandener Ordner und ein Thema ohne thema.yaml sind Fehler."""
    assert "existiert nicht" in fehler_von(tmp_path / "gibt-es-nicht")[0]
    (tmp_path / "x").mkdir()
    assert "thema.yaml fehlt" in fehler_von(tmp_path)[0]


def test_kaputtes_yaml_wird_gemeldet(tmp_path: Path) -> None:
    """Ungültiges YAML führt zu einer Meldung statt zu einem Absturz."""
    thema = schreibe(tmp_path)
    (thema / "01-php-basics" / "01-variablen.yaml").write_text(
        "titel: [unvollständig", encoding="utf-8"
    )

    assert any("nicht lesbar" in meldung for meldung in fehler_von(tmp_path))


def test_weitere_projekte_werden_als_projektaufgaben_angelegt(tmp_path: Path) -> None:
    """Eine Phase kann mehrere Projektaufgaben haben (Abschlussprojekt in Phase 6)."""
    thema = schreibe(tmp_path)
    phase_datei = thema / "01-php-basics" / "phase.yaml"
    daten = yaml.safe_load(phase_datei.read_text(encoding="utf-8"))
    daten["weitere_projekte"] = [{"titel": "Zweites", "beschreibung": "B", "punkte": ["x"]}]
    phase_datei.write_text(yaml.safe_dump(daten), encoding="utf-8")

    importiere_inhalte(tmp_path)

    assert list(m.Projektaufgabe.objects.values_list("titel", "reihenfolge")) == [
        ("Trainingslog", 1),
        ("Zweites", 2),
    ]


def test_befehl_importiert_und_meldet_fehler(tmp_path: Path) -> None:
    """`manage.py import_inhalte` gibt einen Bericht aus bzw. bricht mit Fehlern ab."""
    schreibe(tmp_path)
    ausgabe = StringIO()

    call_command("import_inhalte", str(tmp_path), stdout=ausgabe)

    assert "1 Phasen, 1 Lektionen, 2 Abschnitte, 4 Fragen, 1 Projekte" in ausgabe.getvalue()
    with pytest.raises(CommandError, match="nichts gespeichert"):
        call_command("import_inhalte", str(tmp_path / "gibt-es-nicht"))


def schreibe_lektion(wurzel: Path, name: str, titel: str) -> None:
    """Schreibt eine weitere gültige Lektionsdatei in die erste Phase.

    Args:
        wurzel: Inhaltsordner.
        name: Dateiname, z. B. `02-zweite.yaml`.
        titel: Titel der Lektion.
    """
    daten = lektion_daten()
    daten["titel"] = titel
    (wurzel / "php-laravel" / "01-php-basics" / name).write_text(
        yaml.safe_dump(daten, allow_unicode=True), encoding="utf-8"
    )


def test_umsortieren_von_lektionen_kollidiert_nicht(tmp_path: Path) -> None:
    """Werden zwei Lektionen vertauscht, aktualisiert der Import die Positionen ohne Fehler."""
    schreibe(tmp_path)
    schreibe_lektion(tmp_path, "02-zweite.yaml", "Zweite")
    importiere_inhalte(tmp_path)
    ordner = tmp_path / "php-laravel" / "01-php-basics"
    (ordner / "01-variablen.yaml").rename(ordner / "03-variablen.yaml")
    (ordner / "02-zweite.yaml").rename(ordner / "01-zweite.yaml")
    (ordner / "03-variablen.yaml").rename(ordner / "02-variablen.yaml")

    bericht = importiere_inhalte(tmp_path)

    assert bericht.warnungen == []
    assert list(m.Lektion.objects.values_list("slug", "reihenfolge")) == [
        ("zweite", 1),
        ("variablen", 2),
    ]


def test_umsortieren_von_phasen_und_themen(tmp_path: Path) -> None:
    """Auch Phasen und Themen lassen sich umnummerieren."""
    thema = schreibe(tmp_path)
    zweite = thema / "02-zweite-phase"
    zweite.mkdir()
    (zweite / "phase.yaml").write_text(yaml.safe_dump({"titel": "Zweite"}), encoding="utf-8")
    (zweite / "01-lektion.yaml").write_text(
        yaml.safe_dump(lektion_daten(), allow_unicode=True), encoding="utf-8"
    )
    importiere_inhalte(tmp_path)
    (thema / "01-php-basics").rename(thema / "02-php-basics-neu")
    zweite.rename(thema / "01-zweite-phase")
    (thema / "thema.yaml").write_text(
        yaml.safe_dump({"titel": "PHP/Laravel", "reihenfolge": 5}), encoding="utf-8"
    )
    (thema / "02-php-basics-neu").rename(thema / "02-php-basics")

    importiere_inhalte(tmp_path)

    assert list(m.Phase.objects.values_list("slug", "reihenfolge")) == [
        ("zweite-phase", 1),
        ("php-basics", 2),
    ]
    assert m.Thema.objects.get().reihenfolge == 5


def test_doppelte_nummern_und_kurznamen_werden_gemeldet(tmp_path: Path) -> None:
    """Zwei Lektionen mit gleicher Nummer oder gleichem Kurznamen sind Fehler."""
    schreibe(tmp_path)
    schreibe_lektion(tmp_path, "01-andere.yaml", "Andere")
    schreibe_lektion(tmp_path, "02-variablen.yaml", "Noch eine")

    meldungen = fehler_von(tmp_path)

    assert any("Nummer 01" in meldung for meldung in meldungen)
    assert any("Kurzname „variablen“" in meldung for meldung in meldungen)
    assert m.Lektion.objects.count() == 0


def test_doppelte_phasen_und_themen_nummern(tmp_path: Path) -> None:
    """Gleiche Nummern bei Phasen eines Themas oder bei Themen sind Fehler."""
    thema = schreibe(tmp_path)
    doppelt = thema / "01-andere"
    doppelt.mkdir()
    (doppelt / "phase.yaml").write_text(yaml.safe_dump({"titel": "Andere"}), encoding="utf-8")
    zweites = tmp_path / "englisch"
    zweites.mkdir()
    (zweites / "thema.yaml").write_text(
        yaml.safe_dump({"titel": "Englisch", "reihenfolge": 1}), encoding="utf-8"
    )

    meldungen = fehler_von(tmp_path)

    assert any("Nummer 01" in meldung and "Phase" in meldung for meldung in meldungen)
    assert any("mehreren Themen" in meldung for meldung in meldungen)


def test_richtig_muss_ein_wahrheitswert_sein(tmp_path: Path) -> None:
    """„richtig: ja“ (Text) wird nicht still als falsch gewertet."""
    daten = lektion_daten()
    daten["abschnitte"][0]["quiz"][0]["antworten"][1]["richtig"] = "ja"
    schreibe(tmp_path, daten)

    assert any("true oder false" in meldung for meldung in fehler_von(tmp_path))


def test_doppelte_antworttexte_werden_gemeldet(tmp_path: Path) -> None:
    """Zwei gleiche Antworttexte in einer Frage sind unklar und daher ein Fehler."""
    daten = lektion_daten()
    daten["abschnitte"][0]["quiz"][0]["antworten"][1]["text"] = "A0"
    schreibe(tmp_path, daten)

    assert any("denselben Text" in meldung for meldung in fehler_von(tmp_path))


def test_versteckte_ordner_werden_ignoriert(tmp_path: Path) -> None:
    """Ordner wie `.git` oder `__pycache__` gelten nicht als Thema oder Phase."""
    thema = schreibe(tmp_path)
    (tmp_path / ".git").mkdir()
    (tmp_path / "__pycache__").mkdir()
    (thema / "__pycache__").mkdir()

    assert importiere_inhalte(tmp_path).lektionen == 1


def test_fortschritt_an_quiz_test_und_versuch_bleibt_nach_neuimport(
    tmp_path: Path, nutzer: User
) -> None:
    """Fragen werden neu angelegt; Fortschritt und Testversuch am Quiz/Test bleiben."""
    schreibe(tmp_path)
    importiere_inhalte(tmp_path)
    quiz = m.Quiz.objects.get(abschnitt__reihenfolge=1)
    test = m.Test.objects.get()
    m.Fortschritt.objects.create(nutzer=nutzer, quiz=quiz, punkte=1, max_punkte=1)
    m.Fortschritt.objects.create(nutzer=nutzer, test=test, punkte=1, max_punkte=1)
    m.TestVersuch.objects.create(nutzer=nutzer, test=test)

    importiere_inhalte(tmp_path)

    assert m.Fortschritt.objects.count() == 2
    assert m.TestVersuch.objects.count() == 1
    assert m.Quiz.objects.get(abschnitt__reihenfolge=1).pk == quiz.pk


def test_warnungen_fuer_fehlende_lektion_und_checkpunkte(tmp_path: Path) -> None:
    """Lektionen und Checklistenpunkte ohne Datei-Eintrag werden gemeldet, nicht gelöscht."""
    schreibe(tmp_path)
    schreibe_lektion(tmp_path, "02-zweite.yaml", "Zweite")
    importiere_inhalte(tmp_path)
    ordner = tmp_path / "php-laravel" / "01-php-basics"
    (ordner / "02-zweite.yaml").unlink()
    phase = yaml.safe_load((ordner / "phase.yaml").read_text(encoding="utf-8"))
    phase["projekt"]["punkte"] = ["nur einer"]
    (ordner / "phase.yaml").write_text(yaml.safe_dump(phase), encoding="utf-8")

    bericht = importiere_inhalte(tmp_path)

    assert any("Lektion „zweite“" in w for w in bericht.warnungen)
    assert any("Checklisten-Punkte" in w for w in bericht.warnungen)
    assert m.Lektion.objects.count() == 2
    assert m.ProjektPunkt.objects.count() == 2


def test_echte_inhalte_sind_gueltig() -> None:
    """Die mitgelieferten Inhalte in `backend/inhalte` bestehen alle Prüfungen."""
    wurzel = Path(settings.BASE_DIR) / "inhalte"
    if not wurzel.is_dir():
        pytest.skip("Kein Inhaltsordner vorhanden")

    bericht = importiere_inhalte(wurzel)

    assert bericht.lektionen >= 1
    assert bericht.warnungen == []
    for lektion in m.Lektion.objects.all():
        assert lektion.quellen.exists(), lektion.titel
        assert lektion.test.fragen.count() >= 5, lektion.titel
        assert (lektion.test.zeitlimit_minuten or 0) <= m.TEST_MAX_MINUTEN
