"""Serializer der Lern-API: wandeln Modelle in JSON um und prüfen Eingaben.

Wichtig: Quiz-Serializer geben **nie** preis, welche Antwort richtig ist. Das
erfährt der Nutzer erst in der Auswertung nach der Abgabe.
"""

from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from lernen.models import (
    Abschnitt,
    Antwort,
    Fortschritt,
    Frage,
    Lektion,
    Phase,
    Projektaufgabe,
    Quelle,
    Quiz,
    Thema,
)


class ThemaSerializer(serializers.ModelSerializer[Thema]):
    """Kurzform eines Themas für die Übersicht."""

    class Meta:
        """Felder der Kurzform."""

        model = Thema
        fields = ["id", "titel", "slug", "beschreibung", "reihenfolge"]


class LektionKurzSerializer(serializers.ModelSerializer[Lektion]):
    """Kurzform einer Lektion für die Gliederung einer Phase."""

    class Meta:
        """Felder der Kurzform."""

        model = Lektion
        fields = ["id", "titel", "slug", "zusammenfassung", "reihenfolge"]


class ProjektaufgabeKurzSerializer(serializers.ModelSerializer[Projektaufgabe]):
    """Kurzform einer Projektaufgabe für die Gliederung einer Phase."""

    class Meta:
        """Felder der Kurzform."""

        model = Projektaufgabe
        fields = ["id", "titel", "reihenfolge"]


class PhaseSerializer(serializers.ModelSerializer[Phase]):
    """Phase mit ihren Lektionen und Projektaufgaben."""

    lektionen = LektionKurzSerializer(many=True, read_only=True)
    projektaufgaben = ProjektaufgabeKurzSerializer(many=True, read_only=True)

    class Meta:
        """Felder der Phase."""

        model = Phase
        fields = [
            "id",
            "titel",
            "slug",
            "beschreibung",
            "reihenfolge",
            "lektionen",
            "projektaufgaben",
        ]


class ThemaDetailSerializer(serializers.ModelSerializer[Thema]):
    """Thema mit vollständiger Gliederung (Phasen, Lektionen, Projektaufgaben)."""

    phasen = PhaseSerializer(many=True, read_only=True)

    class Meta:
        """Felder der Detailansicht."""

        model = Thema
        fields = ["id", "titel", "slug", "beschreibung", "reihenfolge", "phasen"]


class QuelleSerializer(serializers.ModelSerializer[Quelle]):
    """Quellenangabe mit Link."""

    class Meta:
        """Felder der Quelle."""

        model = Quelle
        fields = ["titel", "url"]


class AbschnittSerializer(serializers.ModelSerializer[Abschnitt]):
    """Abschnitt mit Lerntext und der ID seines Quiz (falls vorhanden)."""

    quiz_id = serializers.SerializerMethodField()

    class Meta:
        """Felder des Abschnitts."""

        model = Abschnitt
        fields = ["id", "titel", "inhalt", "reihenfolge", "quiz_id"]

    def get_quiz_id(self, abschnitt: Abschnitt) -> int | None:
        """Liefert die ID des Quiz zum Abschnitt.

        Args:
            abschnitt: Der Abschnitt.

        Returns:
            Die Quiz-ID oder None, wenn der Abschnitt (noch) kein Quiz hat.
        """
        try:
            return abschnitt.quiz.id
        except ObjectDoesNotExist:
            return None


class LektionDetailSerializer(serializers.ModelSerializer[Lektion]):
    """Lektion mit Abschnitten, Quellen und der ID ihres Tests (falls vorhanden)."""

    abschnitte = AbschnittSerializer(many=True, read_only=True)
    quellen = QuelleSerializer(many=True, read_only=True)
    test_id = serializers.SerializerMethodField()

    class Meta:
        """Felder der Lektion."""

        model = Lektion
        fields = [
            "id",
            "phase",
            "titel",
            "slug",
            "zusammenfassung",
            "reihenfolge",
            "abschnitte",
            "quellen",
            "test_id",
        ]

    def get_test_id(self, lektion: Lektion) -> int | None:
        """Liefert die ID des Tests zur Lektion.

        Args:
            lektion: Die Lektion.

        Returns:
            Die Test-ID oder None, wenn die Lektion (noch) keinen Test hat.
        """
        try:
            return lektion.test.id
        except ObjectDoesNotExist:
            return None


class AntwortOhneLoesungSerializer(serializers.ModelSerializer[Antwort]):
    """Antwortmöglichkeit **ohne** Angabe, ob sie richtig ist."""

    class Meta:
        """Felder ohne `ist_richtig`."""

        model = Antwort
        fields = ["id", "text", "reihenfolge"]


class FrageOhneLoesungSerializer(serializers.ModelSerializer[Frage]):
    """Frage mit Antwortmöglichkeiten, ohne Lösung und ohne Erklärung."""

    antworten = AntwortOhneLoesungSerializer(many=True, read_only=True)

    class Meta:
        """Felder ohne `erklaerung`."""

        model = Frage
        fields = ["id", "text", "reihenfolge", "antworten"]


class QuizSerializer(serializers.ModelSerializer[Quiz]):
    """Quiz zum Beantworten: Fragen und Antworten ohne Lösung."""

    fragen = FrageOhneLoesungSerializer(many=True, read_only=True)

    class Meta:
        """Felder des Quiz."""

        model = Quiz
        fields = ["id", "abschnitt", "fragen"]


class AuswahlSerializer(serializers.Serializer[dict[str, int]]):
    """Eine beantwortete Frage: welche Antwort zu welcher Frage gewählt wurde."""

    frage = serializers.IntegerField(min_value=1)
    antwort = serializers.IntegerField(min_value=1)


class QuizAbgabeSerializer(serializers.Serializer[dict[str, Any]]):
    """Eingabe einer Quiz-Abgabe: Liste der gewählten Antworten (Fragen dürfen fehlen)."""

    antworten = AuswahlSerializer(many=True)

    def validate_antworten(self, antworten: list[dict[str, int]]) -> list[dict[str, int]]:
        """Stellt sicher, dass jede Frage höchstens einmal beantwortet wird.

        Args:
            antworten: Die geprüften Einzelantworten.

        Returns:
            Die unveränderten Antworten.

        Raises:
            serializers.ValidationError: Wenn eine Frage mehrfach vorkommt.
        """
        fragen = [eintrag["frage"] for eintrag in antworten]
        if len(fragen) != len(set(fragen)):
            raise serializers.ValidationError("Jede Frage darf nur einmal beantwortet werden.")
        return antworten


class FortschrittSerializer(serializers.ModelSerializer[Fortschritt]):
    """Ein Fortschritts-Eintrag des angemeldeten Nutzers."""

    class Meta:
        """Felder des Fortschritts (Ziele als IDs)."""

        model = Fortschritt
        fields = [
            "id",
            "abschnitt",
            "quiz",
            "test",
            "projektaufgabe",
            "punkte",
            "max_punkte",
            "erledigt_am",
        ]
