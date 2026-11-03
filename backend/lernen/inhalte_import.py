"""Import der Lerninhalte aus YAML-Dateien in die Datenbank.

Aufbau des Inhaltsordners (Entscheidung in docs/ENTSCHEIDUNGEN.md, C2)::

    inhalte/<thema>/thema.yaml
    inhalte/<thema>/<NN>-<phase>/phase.yaml        # inkl. Projektaufgabe mit Checkliste
    inhalte/<thema>/<NN>-<phase>/<NN>-<lektion>.yaml  # Quellen, Abschnitte, Quiz, Test

`NN` ist die Reihenfolge (zweistellig), der Rest ist der Kurzname (Slug).

Ablauf: Zuerst wird **alles geprüft**, ohne die Datenbank anzufassen. Erst wenn
keine Fehler gefunden wurden, wird in einer Transaktion gespeichert. Der Import ist
wiederholbar (er aktualisiert statt zu duplizieren) und **löscht nie** Phasen, Lektionen,
Abschnitte, Projekte oder Checklistenpunkte, an denen Fortschritt hängen kann. Fehlen
Lektionen, Abschnitte oder Checklistenpunkte in den Dateien, wird nur gewarnt. Quellen,
Fragen und Antworten werden dagegen ersetzt (an ihnen hängt kein Fortschritt).

Abschnitte, Projekte und Checklistenpunkte werden über ihre **Position** erkannt, Phasen und
Lektionen über ihren Kurznamen. Neue Abschnitte und Punkte daher nur **hinten anhängen**,
sonst zeigt vorhandener Fortschritt auf anderen Inhalt (siehe docs/ENTSCHEIDUNGEN.md, C2).

Geprüft werden hier die Regeln, die die Datenbank nicht erzwingen kann
(docs/ENTSCHEIDUNGEN.md, B1): jede Lektion hat mindestens eine Quelle mit
http(s)-Link, jede Frage genau eine richtige Antwort.
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import transaction
from django.db.models import F, QuerySet

from lernen import models as m

logger = logging.getLogger(__name__)

_NAME = re.compile(r"^(\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)$")
_URL_PRUEFER = URLValidator(schemes=["http", "https"])
#: Verschiebung, mit der Positionen vorübergehend aus dem Weg geräumt werden.
_VERSCHIEBUNG = 1_000_000


class InhaltsFehler(Exception):
    """Die Inhaltsdateien enthalten Fehler; nichts wurde gespeichert.

    Attributes:
        meldungen: Alle gefundenen Fehler, je mit Datei und Beschreibung.
    """

    def __init__(self, meldungen: list[str]) -> None:
        """Merkt sich die Fehlermeldungen.

        Args:
            meldungen: Alle gefundenen Fehler.
        """
        super().__init__(f"{len(meldungen)} Fehler in den Inhaltsdateien")
        self.meldungen = meldungen


@dataclass
class ImportBericht:
    """Ergebnis eines Imports.

    Attributes:
        phasen: Anzahl verarbeiteter Phasen.
        lektionen: Anzahl verarbeiteter Lektionen (Themenfelder).
        abschnitte: Anzahl verarbeiteter Abschnitte (je mit Quiz).
        fragen: Anzahl Fragen in Quizzen und Tests.
        projekte: Anzahl verarbeiteter Projektaufgaben.
        warnungen: Hinweise, z. B. Inhalte in der Datenbank ohne Datei.
    """

    phasen: int = 0
    lektionen: int = 0
    abschnitte: int = 0
    fragen: int = 0
    projekte: int = 0
    warnungen: list[str] = field(default_factory=list)


def _lese_yaml(datei: Path, fehler: list[str]) -> dict[str, Any] | None:
    """Liest eine YAML-Datei, die ein Objekt (Zuordnung) enthalten muss.

    Args:
        datei: Pfad der Datei.
        fehler: Liste, an die Fehlermeldungen angehängt werden.

    Returns:
        Den Inhalt als Dictionary oder None bei Lese- bzw. Formatfehlern.
    """
    try:
        daten = yaml.safe_load(datei.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as ex:
        fehler.append(f"{datei}: Datei nicht lesbar ({ex})")
        return None
    if not isinstance(daten, dict):
        fehler.append(f"{datei}: erwartet ein Objekt auf oberster Ebene")
        return None
    return daten


def _text(
    daten: dict[str, Any],
    schluessel: str,
    ort: str,
    fehler: list[str],
    *,
    pflicht: bool = True,
    maximal: int | None = None,
) -> str:
    """Liest ein Textfeld und prüft Pflicht und Länge.

    Args:
        daten: Das Objekt, in dem das Feld steht.
        schluessel: Name des Felds.
        ort: Fundstelle für die Fehlermeldung.
        fehler: Liste, an die Fehlermeldungen angehängt werden.
        pflicht: Ob das Feld nicht leer sein darf.
        maximal: Höchstlänge in Zeichen oder None.

    Returns:
        Den Text ohne Leerzeichen am Rand (leer, wenn nicht vorhanden oder fehlerhaft).
    """
    wert = daten.get(schluessel)
    if wert is None:
        wert = ""
    if not isinstance(wert, str):
        fehler.append(f"{ort}: „{schluessel}“ muss Text sein")
        return ""
    wert = wert.strip()
    if pflicht and not wert:
        fehler.append(f"{ort}: „{schluessel}“ fehlt oder ist leer")
    if maximal is not None and len(wert) > maximal:
        fehler.append(f"{ort}: „{schluessel}“ ist länger als {maximal} Zeichen")
    return wert


def _liste(daten: dict[str, Any], schluessel: str, ort: str, fehler: list[str]) -> list[Any]:
    """Liest eine Liste, die mindestens ein Element haben muss.

    Args:
        daten: Das Objekt, in dem das Feld steht.
        schluessel: Name des Felds.
        ort: Fundstelle für die Fehlermeldung.
        fehler: Liste, an die Fehlermeldungen angehängt werden.

    Returns:
        Die Liste (leer bei fehlendem oder fehlerhaftem Feld).
    """
    wert = daten.get(schluessel)
    if not isinstance(wert, list) or not wert:
        fehler.append(f"{ort}: „{schluessel}“ muss eine nicht leere Liste sein")
        return []
    return wert


@dataclass
class _Frage:
    """Geprüfte Frage mit Antworten (richtige Antwort als Index)."""

    text: str
    erklaerung: str
    antworten: list[str]
    richtig: int


def _pruefe_fragen(roh: list[Any], ort: str, fehler: list[str]) -> list[_Frage]:
    """Prüft eine Liste von Fragen.

    Args:
        roh: Die Fragen aus der YAML-Datei.
        ort: Fundstelle für Fehlermeldungen.
        fehler: Liste, an die Fehlermeldungen angehängt werden.

    Returns:
        Die geprüften Fragen (fehlerhafte Fragen werden ausgelassen).
    """
    ergebnis: list[_Frage] = []
    for nr, eintrag in enumerate(roh, start=1):
        stelle = f"{ort}, Frage {nr}"
        if not isinstance(eintrag, dict):
            fehler.append(f"{stelle}: erwartet ein Objekt")
            continue
        vorher = len(fehler)
        text = _text(eintrag, "frage", stelle, fehler)
        erklaerung = _text(eintrag, "erklaerung", stelle, fehler, pflicht=False)
        antworten_roh = _liste(eintrag, "antworten", stelle, fehler)
        if len(antworten_roh) == 1:
            fehler.append(f"{stelle}: mindestens zwei Antworten nötig")
        texte: list[str] = []
        richtige: list[int] = []
        for i, antwort in enumerate(antworten_roh):
            if not isinstance(antwort, dict):
                fehler.append(f"{stelle}, Antwort {i + 1}: erwartet ein Objekt")
                continue
            texte.append(_text(antwort, "text", f"{stelle}, Antwort {i + 1}", fehler, maximal=500))
            richtig = antwort.get("richtig", False)
            if not isinstance(richtig, bool):
                fehler.append(f"{stelle}, Antwort {i + 1}: „richtig“ muss true oder false sein")
            elif richtig:
                richtige.append(len(texte) - 1)
        if len(set(texte)) != len(texte):
            fehler.append(f"{stelle}: zwei Antworten haben denselben Text")
        if len(richtige) != 1:
            fehler.append(
                f"{stelle}: genau eine Antwort muss „richtig: true“ sein "
                f"(gefunden: {len(richtige)})"
            )
        if len(fehler) == vorher:
            ergebnis.append(_Frage(text, erklaerung, texte, richtige[0]))
    return ergebnis


@dataclass
class _Abschnitt:
    """Geprüfter Abschnitt mit Quiz."""

    titel: str
    inhalt: str
    quiz: list[_Frage]


@dataclass
class _Lektion:
    """Geprüfte Lektion mit Quellen, Abschnitten und Test."""

    reihenfolge: int
    slug: str
    titel: str
    zusammenfassung: str
    quellen: list[tuple[str, str]]
    abschnitte: list[_Abschnitt]
    zeitlimit: int
    test: list[_Frage]


@dataclass
class _Projekt:
    """Geprüfte Projektaufgabe mit Checkliste."""

    titel: str
    beschreibung: str
    punkte: list[str]


@dataclass
class _Phase:
    """Geprüfte Phase mit Lektionen und optionalem Projekt."""

    reihenfolge: int
    slug: str
    titel: str
    beschreibung: str
    projekte: list[_Projekt]
    lektionen: list[_Lektion]


def _pruefe_lektion(datei: Path, nummer: int, slug: str, fehler: list[str]) -> _Lektion | None:
    """Liest und prüft eine Lektionsdatei.

    Args:
        datei: Pfad der Datei.
        nummer: Reihenfolge aus dem Dateinamen.
        slug: Kurzname aus dem Dateinamen.
        fehler: Liste, an die Fehlermeldungen angehängt werden.

    Returns:
        Die geprüfte Lektion oder None, wenn die Datei nicht lesbar ist.
    """
    daten = _lese_yaml(datei, fehler)
    if daten is None:
        return None
    ort = str(datei)
    titel = _text(daten, "titel", ort, fehler, maximal=200)
    zusammenfassung = _text(daten, "zusammenfassung", ort, fehler, pflicht=False)

    quellen: list[tuple[str, str]] = []
    for nr, quelle in enumerate(_liste(daten, "quellen", ort, fehler), start=1):
        stelle = f"{ort}, Quelle {nr}"
        if not isinstance(quelle, dict):
            fehler.append(f"{stelle}: erwartet ein Objekt")
            continue
        q_titel = _text(quelle, "titel", stelle, fehler, maximal=300)
        url = _text(quelle, "url", stelle, fehler, maximal=500)
        try:
            _URL_PRUEFER(url)
        except ValidationError:
            fehler.append(f"{stelle}: „url“ ist kein gültiger http(s)-Link ({url})")
        quellen.append((q_titel, url))
    if len({url for _, url in quellen}) != len(quellen):
        fehler.append(f"{ort}: dieselbe Quelle ist mehrfach eingetragen")

    abschnitte: list[_Abschnitt] = []
    for nr, abschnitt in enumerate(_liste(daten, "abschnitte", ort, fehler), start=1):
        stelle = f"{ort}, Abschnitt {nr}"
        if not isinstance(abschnitt, dict):
            fehler.append(f"{stelle}: erwartet ein Objekt")
            continue
        a_titel = _text(abschnitt, "titel", stelle, fehler, maximal=200)
        inhalt = _text(abschnitt, "inhalt", stelle, fehler)
        quiz = _pruefe_fragen(_liste(abschnitt, "quiz", stelle, fehler), f"{stelle}, Quiz", fehler)
        abschnitte.append(_Abschnitt(a_titel, inhalt, quiz))

    test_roh = daten.get("test")
    zeitlimit = m.TEST_MAX_MINUTEN
    test: list[_Frage] = []
    if not isinstance(test_roh, dict):
        fehler.append(f"{ort}: „test“ fehlt (Test nach jedem Themenfeld)")
    else:
        wert = test_roh.get("zeitlimit_minuten", m.TEST_MAX_MINUTEN)
        if isinstance(wert, int) and not isinstance(wert, bool) and 1 <= wert <= m.TEST_MAX_MINUTEN:
            zeitlimit = wert
        else:
            fehler.append(
                f"{ort}, Test: „zeitlimit_minuten“ muss eine Zahl "
                f"von 1 bis {m.TEST_MAX_MINUTEN} sein"
            )
        test = _pruefe_fragen(
            _liste(test_roh, "fragen", f"{ort}, Test", fehler), f"{ort}, Test", fehler
        )
    return _Lektion(nummer, slug, titel, zusammenfassung, quellen, abschnitte, zeitlimit, test)


def _pruefe_projekt(roh: Any, ort: str, fehler: list[str]) -> _Projekt | None:
    """Prüft die Projektaufgabe einer Phase.

    Args:
        roh: Der Wert von „projekt“ aus phase.yaml.
        ort: Fundstelle für Fehlermeldungen.
        fehler: Liste, an die Fehlermeldungen angehängt werden.

    Returns:
        Das geprüfte Projekt oder None bei Formfehlern.
    """
    if not isinstance(roh, dict):
        fehler.append(f"{ort}: „projekt“ muss ein Objekt sein")
        return None
    titel = _text(roh, "titel", ort, fehler, maximal=200)
    beschreibung = _text(roh, "beschreibung", ort, fehler)
    punkte: list[str] = []
    for nr, punkt in enumerate(_liste(roh, "punkte", ort, fehler), start=1):
        if not isinstance(punkt, str) or not punkt.strip() or len(punkt.strip()) > 300:
            fehler.append(f"{ort}, Punkt {nr}: Text von 1 bis 300 Zeichen erwartet")
        else:
            punkte.append(punkt.strip())
    return _Projekt(titel, beschreibung, punkte)


def _benenne(pfad: Path, endung: str, fehler: list[str]) -> tuple[int, str] | None:
    """Zerlegt „NN-kurzname“ aus einem Datei- oder Ordnernamen.

    Args:
        pfad: Datei oder Ordner.
        endung: Dateiendung, die zuerst entfernt wird (leer bei Ordnern).
        fehler: Liste, an die Fehlermeldungen angehängt werden.

    Returns:
        Reihenfolge und Slug oder None, wenn der Name nicht passt.
    """
    name = pfad.name.removesuffix(endung)
    treffer = _NAME.match(name)
    if not treffer:
        fehler.append(
            f"{pfad}: Name muss die Form „01-kurzname“ haben "
            "(Kleinbuchstaben, Ziffern, Bindestriche)"
        )
        return None
    return int(treffer.group(1)), treffer.group(2)


def _pruefe_eindeutig(
    eintraege: list[tuple[int, str]], ort: str, art: str, fehler: list[str]
) -> None:
    """Meldet doppelte Nummern oder Kurznamen unter Geschwistern.

    Args:
        eintraege: Paare aus Nummer und Kurzname, z. B. aller Lektionen einer Phase.
        ort: Fundstelle für die Fehlermeldung (Ordner).
        art: Bezeichnung, z. B. „Lektion“.
        fehler: Liste, an die Fehlermeldungen angehängt werden.
    """
    nummern = [nummer for nummer, _ in eintraege]
    slugs = [slug for _, slug in eintraege]
    for nummer in sorted({n for n in nummern if nummern.count(n) > 1}):
        fehler.append(f"{ort}: Nummer {nummer:02d} kommt bei mehreren {art}-Einträgen vor")
    for slug in sorted({s for s in slugs if slugs.count(s) > 1}):
        fehler.append(f"{ort}: Kurzname „{slug}“ kommt bei mehreren {art}-Einträgen vor")


def _ist_inhalt(pfad: Path) -> bool:
    """Entscheidet, ob ein Eintrag im Inhaltsordner ein Ordner mit Inhalt ist.

    Args:
        pfad: Eintrag im Verzeichnis.

    Returns:
        True für Ordner, deren Name nicht mit „.“ oder „_“ beginnt (nicht `.git`, `__pycache__`).
    """
    return pfad.is_dir() and not pfad.name.startswith((".", "_"))


def _lese_thema(ordner: Path, fehler: list[str]) -> tuple[dict[str, Any], list[_Phase]] | None:
    """Liest ein Thema mit allen Phasen und prüft es.

    Args:
        ordner: Ordner des Themas (enthält thema.yaml).
        fehler: Liste, an die Fehlermeldungen angehängt werden.

    Returns:
        Die Daten aus thema.yaml (Titel, Slug, ...) und die Phasen, oder None.
    """
    datei = ordner / "thema.yaml"
    if not datei.is_file():
        fehler.append(f"{ordner}: thema.yaml fehlt")
        return None
    thema = _lese_yaml(datei, fehler)
    if thema is None:
        return None
    _text(thema, "titel", str(datei), fehler, maximal=200)
    reihenfolge = thema.get("reihenfolge")
    if not isinstance(reihenfolge, int) or isinstance(reihenfolge, bool) or reihenfolge < 1:
        fehler.append(f"{datei}: „reihenfolge“ muss eine positive Zahl sein")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", ordner.name):
        fehler.append(f"{ordner}: Ordnername muss ein Kurzname sein (Kleinbuchstaben, Ziffern, -)")
    if not isinstance(thema.get("beschreibung") or "", str):
        fehler.append(f"{datei}: „beschreibung“ muss Text sein")
    thema["slug"] = ordner.name
    phasen: list[_Phase] = []
    for phasen_ordner in sorted(p for p in ordner.iterdir() if _ist_inhalt(p)):
        benannt = _benenne(phasen_ordner, "", fehler)
        phase_datei = phasen_ordner / "phase.yaml"
        if benannt is None:
            continue
        if not phase_datei.is_file():
            fehler.append(f"{phasen_ordner}: phase.yaml fehlt")
            continue
        daten = _lese_yaml(phase_datei, fehler)
        if daten is None:
            continue
        projekte: list[_Projekt] = []
        if "projekt" in daten:
            projekt = _pruefe_projekt(daten["projekt"], f"{phase_datei}, Projekt", fehler)
            if projekt is not None:
                projekte.append(projekt)
        for extra in daten.get("weitere_projekte", []) or []:
            projekt = _pruefe_projekt(extra, f"{phase_datei}, weiteres Projekt", fehler)
            if projekt is not None:
                projekte.append(projekt)
        lektionen: list[_Lektion] = []
        for lektions_datei in sorted(phasen_ordner.glob("*.yaml")):
            if lektions_datei.name == "phase.yaml":
                continue
            lektion_name = _benenne(lektions_datei, ".yaml", fehler)
            if lektion_name is None:
                continue
            lektion = _pruefe_lektion(lektions_datei, lektion_name[0], lektion_name[1], fehler)
            if lektion is not None:
                lektionen.append(lektion)
        _pruefe_eindeutig(
            [(lektion.reihenfolge, lektion.slug) for lektion in lektionen],
            str(phasen_ordner),
            "Lektion",
            fehler,
        )
        phasen.append(
            _Phase(
                benannt[0],
                benannt[1],
                _text(daten, "titel", str(phase_datei), fehler, maximal=200),
                _text(daten, "beschreibung", str(phase_datei), fehler, pflicht=False),
                projekte,
                lektionen,
            )
        )
    _pruefe_eindeutig(
        [(phase.reihenfolge, phase.slug) for phase in phasen], str(ordner), "Phase", fehler
    )
    return thema, phasen


def _raeume_reihenfolge_frei(eintraege: QuerySet[Any]) -> None:
    """Verschiebt vorhandene Positionen vorübergehend, damit Umsortieren nicht kollidiert.

    Die Datenbank erlaubt jede Position nur einmal. Beim Vertauschen zweier Einträge würde
    sonst einer kurz auf die Position des anderen treffen. Verschoben wird auf einen Wert,
    der pro Eintrag eindeutig ist; die Endwerte setzt der Import danach selbst.
    Einträge, die nicht mehr in den Dateien stehen, behalten die hohe Position (sie
    werden ans Ende sortiert und als Warnung gemeldet).

    Args:
        eintraege: Die Einträge, deren Positionen frei gemacht werden.
    """
    eintraege.filter(reihenfolge__lt=_VERSCHIEBUNG).update(reihenfolge=F("id") + _VERSCHIEBUNG)


def _speichere_fragen(ziel: dict[str, Any], fragen: list[_Frage]) -> None:
    """Ersetzt alle Fragen eines Quiz bzw. Tests durch die geprüften Fragen.

    Fragen und Antworten werden neu angelegt; Fortschritt verweist nur auf Quiz und Test,
    nicht auf einzelne Fragen, daher geht dabei nichts verloren.

    Args:
        ziel: `{"quiz": quiz}` oder `{"test": test}`.
        fragen: Die geprüften Fragen in Reihenfolge.
    """
    m.Frage.objects.filter(**ziel).delete()
    for nr, frage in enumerate(fragen, start=1):
        gespeichert = m.Frage.objects.create(
            **ziel, text=frage.text, erklaerung=frage.erklaerung, reihenfolge=nr
        )
        for i, text in enumerate(frage.antworten):
            m.Antwort.objects.create(
                frage=gespeichert, text=text, ist_richtig=(i == frage.richtig), reihenfolge=i + 1
            )


def _speichere_lektion(phase: m.Phase, daten: _Lektion, bericht: ImportBericht) -> None:
    """Legt eine Lektion samt Quellen, Abschnitten, Quizzen und Test an oder aktualisiert sie.

    Args:
        phase: Die zugehörige Phase.
        daten: Die geprüfte Lektion.
        bericht: Bericht, in dem gezählt und gewarnt wird.
    """
    lektion, _ = m.Lektion.objects.update_or_create(
        phase=phase,
        slug=daten.slug,
        defaults={
            "titel": daten.titel,
            "zusammenfassung": daten.zusammenfassung,
            "reihenfolge": daten.reihenfolge,
        },
    )
    lektion.quellen.all().delete()
    for titel, url in daten.quellen:
        m.Quelle.objects.create(lektion=lektion, titel=titel, url=url)
    for nr, abschnitt in enumerate(daten.abschnitte, start=1):
        gespeichert, _ = m.Abschnitt.objects.update_or_create(
            lektion=lektion,
            reihenfolge=nr,
            defaults={"titel": abschnitt.titel, "inhalt": abschnitt.inhalt},
        )
        quiz, _ = m.Quiz.objects.get_or_create(abschnitt=gespeichert)
        _speichere_fragen({"quiz": quiz}, abschnitt.quiz)
        bericht.abschnitte += 1
        bericht.fragen += len(abschnitt.quiz)
    ueberzaehlig = lektion.abschnitte.filter(reihenfolge__gt=len(daten.abschnitte)).count()
    if ueberzaehlig:
        bericht.warnungen.append(
            f"Lektion „{daten.titel}“: {ueberzaehlig} Abschnitt(e) in der Datenbank "
            "ohne Eintrag in der Datei (nicht gelöscht)"
        )
    test, _ = m.Test.objects.update_or_create(
        lektion=lektion, defaults={"zeitlimit_minuten": daten.zeitlimit}
    )
    _speichere_fragen({"test": test}, daten.test)
    bericht.fragen += len(daten.test)
    bericht.lektionen += 1


def _speichere_projekt(phase: m.Phase, nr: int, projekt: _Projekt, bericht: ImportBericht) -> None:
    """Legt eine Projektaufgabe mit Checkliste an oder aktualisiert sie.

    Args:
        phase: Die zugehörige Phase.
        nr: Reihenfolge innerhalb der Phase.
        projekt: Das geprüfte Projekt.
        bericht: Bericht, in dem gezählt und gewarnt wird.
    """
    gespeichert, _ = m.Projektaufgabe.objects.update_or_create(
        phase=phase,
        reihenfolge=nr,
        defaults={"titel": projekt.titel, "beschreibung": projekt.beschreibung},
    )
    for pnr, text in enumerate(projekt.punkte, start=1):
        m.ProjektPunkt.objects.update_or_create(
            projektaufgabe=gespeichert, reihenfolge=pnr, defaults={"text": text}
        )
    if gespeichert.punkte.filter(reihenfolge__gt=len(projekt.punkte)).exists():
        bericht.warnungen.append(
            f"Projekt „{projekt.titel}“: Checklisten-Punkte in der Datenbank "
            "ohne Eintrag in der Datei (nicht gelöscht)"
        )
    bericht.projekte += 1


def importiere_inhalte(wurzel: Path) -> ImportBericht:
    """Prüft alle Inhaltsdateien und speichert sie, wenn sie fehlerfrei sind.

    Args:
        wurzel: Ordner, der die Themen-Ordner enthält (z. B. `backend/inhalte`).

    Returns:
        Den Bericht mit Zählwerten und Warnungen.

    Raises:
        InhaltsFehler: Wenn Dateien fehlerhaft sind. Dann wurde nichts gespeichert.
    """
    fehler: list[str] = []
    if not wurzel.is_dir():
        raise InhaltsFehler([f"{wurzel}: Ordner existiert nicht"])
    themen = [
        gelesen
        for ordner in sorted(p for p in wurzel.iterdir() if _ist_inhalt(p))
        if (gelesen := _lese_thema(ordner, fehler)) is not None
    ]
    nummern = [daten["reihenfolge"] for daten, _ in themen]
    for nummer in sorted({n for n in nummern if nummern.count(n) > 1}):
        fehler.append(f"{wurzel}: „reihenfolge“ {nummer} kommt bei mehreren Themen vor")
    if fehler:
        raise InhaltsFehler(fehler)

    bericht = ImportBericht()
    with transaction.atomic():
        _raeume_reihenfolge_frei(m.Thema.objects.all())
        for daten, phasen in themen:
            thema, _ = m.Thema.objects.update_or_create(
                slug=daten["slug"],
                defaults={
                    "titel": str(daten["titel"]).strip(),
                    "beschreibung": str(daten.get("beschreibung") or "").strip(),
                    "reihenfolge": daten["reihenfolge"],
                },
            )
            _raeume_reihenfolge_frei(thema.phasen.all())
            for phase_daten in phasen:
                phase, _ = m.Phase.objects.update_or_create(
                    thema=thema,
                    slug=phase_daten.slug,
                    defaults={
                        "titel": phase_daten.titel,
                        "beschreibung": phase_daten.beschreibung,
                        "reihenfolge": phase_daten.reihenfolge,
                    },
                )
                bericht.phasen += 1
                _raeume_reihenfolge_frei(phase.lektionen.all())
                for lektion in phase_daten.lektionen:
                    _speichere_lektion(phase, lektion, bericht)
                for nr, projekt in enumerate(phase_daten.projekte, start=1):
                    _speichere_projekt(phase, nr, projekt, bericht)
                vorhanden = set(phase.lektionen.values_list("slug", flat=True))
                fehlend = vorhanden - {lektion.slug for lektion in phase_daten.lektionen}
                for slug in sorted(fehlend):
                    bericht.warnungen.append(
                        f"Phase „{phase.titel}“: Lektion „{slug}“ in der Datenbank "
                        "ohne Datei (nicht gelöscht)"
                    )
    logger.info(
        "Inhalte importiert: %d Phasen, %d Lektionen, %d Abschnitte, %d Fragen, %d Projekte",
        bericht.phasen,
        bericht.lektionen,
        bericht.abschnitte,
        bericht.fragen,
        bericht.projekte,
    )
    return bericht
