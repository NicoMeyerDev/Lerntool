"""API-Views der Lern-App. Nur Ein- und Ausgabe; die Logik liegt in `lernen.services`."""

from dataclasses import asdict
from datetime import date
from typing import Any

from django.conf import settings
from django.db.models import Prefetch, QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.anmeldung import angemeldeter_nutzer
from lernen.dashboard import erstelle_dashboard
from lernen.models import (
    Abschnitt,
    Fortschritt,
    Frage,
    Lektion,
    Phase,
    Projektaufgabe,
    ProjektPunkt,
    Quiz,
    Test,
    Thema,
)
from lernen.serializers import (
    FortschrittSerializer,
    LektionDetailSerializer,
    ProjektPunktSerializer,
    ProjektPunktSetzenSerializer,
    QuizAbgabeSerializer,
    QuizSerializer,
    TestSerializer,
    ThemaDetailSerializer,
    ThemaSerializer,
)
from lernen.services import (
    ProjektStand,
    TestZeitAbgelaufen,
    UngueltigeAbgabe,
    markiere_abschnitt_gelesen,
    projekt_stand,
    setze_projektpunkt,
    starte_test,
    werte_quiz_aus,
    werte_test_aus,
)
from lernen.wochenplan import MAX_JAHR, MIN_JAHR, erstelle_wochenplan


class ThemaListeView(generics.ListAPIView[Thema]):
    """`GET /api/themen/`: alle Themen in fester Reihenfolge."""

    queryset = Thema.objects.all()
    serializer_class = ThemaSerializer


class ThemaDetailView(generics.RetrieveAPIView[Thema]):
    """`GET /api/themen/<slug>/`: ein Thema mit Phasen, Lektionen und Projektaufgaben."""

    serializer_class = ThemaDetailSerializer
    lookup_field = "slug"
    queryset = Thema.objects.prefetch_related(
        Prefetch(
            "phasen",
            queryset=Phase.objects.prefetch_related("lektionen", "projektaufgaben"),
        )
    )


class LektionDetailView(generics.RetrieveAPIView[Lektion]):
    """`GET /api/lektionen/<id>/`: Lektion mit Abschnitten, Quellen, Quiz- und Test-ID."""

    serializer_class = LektionDetailSerializer
    queryset = Lektion.objects.select_related("test").prefetch_related(
        Prefetch("abschnitte", queryset=Abschnitt.objects.select_related("quiz")), "quellen"
    )


def _quizze_mit_fragen() -> QuerySet[Quiz]:
    """Quizze mit vorgeladenen Fragen und Antworten.

    Returns:
        Ein QuerySet, das Fragen und Antworten in wenigen Abfragen lädt.
    """
    return Quiz.objects.prefetch_related(
        Prefetch("fragen", queryset=Frage.objects.prefetch_related("antworten"))
    )


class QuizDetailView(generics.RetrieveAPIView[Quiz]):
    """`GET /api/quizze/<id>/`: Fragen und Antwortmöglichkeiten **ohne** Lösung."""

    serializer_class = QuizSerializer

    def get_queryset(self) -> QuerySet[Quiz]:
        """Liefert die Quizze mit vorgeladenen Fragen und Antworten."""
        return _quizze_mit_fragen()


class QuizAbgabeView(APIView):
    """`POST /api/quizze/<id>/abgabe/`: Antworten abgeben, Auswertung erhalten."""

    def post(self, request: Request, pk: int) -> Response:
        """Wertet die Abgabe aus und speichert den Bestwert als Fortschritt.

        Args:
            request: Anfrage mit `{"antworten": [{"frage": <id>, "antwort": <id>}, ...]}`.
            pk: ID des Quiz.

        Returns:
            200 mit Punkten, Bestwert und Auswertung je Frage; 400 bei ungültiger
            Abgabe; 404, wenn es das Quiz nicht gibt.
        """
        quiz = get_object_or_404(Quiz, pk=pk)
        eingabe = QuizAbgabeSerializer(data=request.data)
        eingabe.is_valid(raise_exception=True)
        auswahl = {
            eintrag["frage"]: eintrag["antwort"] for eintrag in eingabe.validated_data["antworten"]
        }
        try:
            ergebnis = werte_quiz_aus(quiz, angemeldeter_nutzer(request), auswahl)
        except UngueltigeAbgabe as fehler:
            return Response({"detail": str(fehler)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(asdict(ergebnis))


class AbschnittGelesenView(APIView):
    """`POST /api/abschnitte/<id>/gelesen/`: Abschnitt als gelesen markieren."""

    def post(self, request: Request, pk: int) -> Response:
        """Speichert, dass der angemeldete Nutzer den Abschnitt gelesen hat.

        Args:
            request: Die Anfrage (ohne Inhalt).
            pk: ID des Abschnitts.

        Returns:
            200 mit dem Fortschritts-Eintrag; 404, wenn es den Abschnitt nicht gibt.
        """
        abschnitt = get_object_or_404(Abschnitt, pk=pk)
        fortschritt = markiere_abschnitt_gelesen(abschnitt, angemeldeter_nutzer(request))
        return Response(FortschrittSerializer(fortschritt).data)


class FortschrittListeView(generics.ListAPIView[Fortschritt]):
    """`GET /api/fortschritt/`: alle Fortschritts-Einträge des angemeldeten Nutzers."""

    serializer_class = FortschrittSerializer

    def get_queryset(self) -> QuerySet[Fortschritt]:
        """Liefert nur die Einträge des angemeldeten Nutzers."""
        return Fortschritt.objects.filter(nutzer=angemeldeter_nutzer(self.request))


class DashboardView(APIView):
    """`GET /api/dashboard/`: Statistiken, XP, Level, Abzeichen und Meilensteine."""

    def get(self, request: Request) -> Response:
        """Berechnet das Dashboard des angemeldeten Nutzers.

        Args:
            request: Die Anfrage.

        Returns:
            200 mit XP, Level, Statistik, Themenfortschritt, Abzeichen und Meilensteinen.
        """
        return Response(asdict(erstelle_dashboard(angemeldeter_nutzer(request))))


class WochenplanView(APIView):
    """`GET /api/wochenplan/?datum=JJJJ-MM-TT`: Plan und Auswertung einer Lernwoche."""

    def get(self, request: Request) -> Response:
        """Liefert die Woche, in der `datum` liegt (ohne Angabe: die aktuelle Woche).

        Args:
            request: Die Anfrage mit optionalem Parameter `datum`.

        Returns:
            200 mit dem Wochenplan, 400 bei ungültigem Datum.
        """
        heute = timezone.localdate()
        text = request.query_params.get("datum")
        tag = heute
        if text is not None:
            try:
                gewuenscht: date | None = date.fromisoformat(text)
            except ValueError:
                gewuenscht = None
            if gewuenscht is None or not MIN_JAHR <= gewuenscht.year <= MAX_JAHR:
                return Response(
                    {"datum": f"Ungültiges Datum, erwartet JJJJ-MM-TT ({MIN_JAHR}–{MAX_JAHR})."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            tag = gewuenscht
        plan = erstelle_wochenplan(angemeldeter_nutzer(request), tag, heute, settings.LERNSTART)
        return Response(asdict(plan))


class TestDetailView(generics.RetrieveAPIView[Test]):
    """`GET /api/tests/<id>/`: Fragen und Antwortmöglichkeiten **ohne** Lösung."""

    __test__ = False  # Kein pytest-Testfall, trotz des Namens.

    serializer_class = TestSerializer

    def get_queryset(self) -> QuerySet[Test]:
        """Liefert die Tests mit vorgeladenen Fragen und Antworten."""
        return Test.objects.prefetch_related(
            Prefetch("fragen", queryset=Frage.objects.prefetch_related("antworten"))
        )


class TestStartView(APIView):
    """`POST /api/tests/<id>/start/`: Testversuch starten oder fortsetzen."""

    __test__ = False  # Kein pytest-Testfall, trotz des Namens.

    def post(self, request: Request, pk: int) -> Response:
        """Startet den Zeitlimit-Zähler auf dem Server.

        Args:
            request: Die Anfrage (ohne Inhalt).
            pk: ID des Tests.

        Returns:
            200 mit Versuchs-ID, Start, Ende und Restzeit in Sekunden; 404, wenn es
            den Test nicht gibt.
        """
        test = get_object_or_404(Test, pk=pk)
        return Response(asdict(starte_test(test, angemeldeter_nutzer(request))))


class TestAbgabeView(APIView):
    """`POST /api/tests/<id>/abgabe/`: Antworten des laufenden Versuchs abgeben."""

    __test__ = False  # Kein pytest-Testfall, trotz des Namens.

    def post(self, request: Request, pk: int) -> Response:
        """Wertet die Abgabe aus, wenn das Zeitlimit eingehalten wurde.

        Args:
            request: Anfrage mit `{"antworten": [{"frage": <id>, "antwort": <id>}, ...]}`.
            pk: ID des Tests.

        Returns:
            200 mit Punkten, Bestwert und Auswertung je Frage; 400 bei ungültiger
            Abgabe; 409, wenn kein Versuch läuft oder die Zeit abgelaufen ist; 404,
            wenn es den Test nicht gibt.
        """
        test = get_object_or_404(Test, pk=pk)
        eingabe = QuizAbgabeSerializer(data=request.data)
        eingabe.is_valid(raise_exception=True)
        auswahl = {
            eintrag["frage"]: eintrag["antwort"] for eintrag in eingabe.validated_data["antworten"]
        }
        try:
            ergebnis = werte_test_aus(test, angemeldeter_nutzer(request), auswahl)
        except TestZeitAbgelaufen as fehler:
            return Response({"detail": str(fehler)}, status=status.HTTP_409_CONFLICT)
        except UngueltigeAbgabe as fehler:
            return Response({"detail": str(fehler)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(asdict(ergebnis))


def _projekt_antwort(projekt: Projektaufgabe, stand: ProjektStand) -> dict[str, Any]:
    """Baut die Antwort für eine Projektaufgabe samt Stand des Nutzers.

    Args:
        projekt: Die Projektaufgabe.
        stand: Der Stand des angemeldeten Nutzers.

    Returns:
        Aufgabe, Checkliste mit Haken und Auswertung (erledigt, gesamt, abgeschlossen).
    """
    punkte = [
        {**punkt, "erledigt": punkt["id"] in stand.erledigt_ids}
        for punkt in ProjektPunktSerializer(projekt.punkte.all(), many=True).data
    ]
    return {
        "id": projekt.id,
        "phase": projekt.phase_id,
        "titel": projekt.titel,
        "beschreibung": projekt.beschreibung,
        "punkte": punkte,
        "erledigt": stand.erledigt,
        "gesamt": stand.gesamt,
        "abgeschlossen": stand.abgeschlossen,
    }


class ProjektDetailView(APIView):
    """`GET /api/projekte/<id>/`: Projektaufgabe mit Checkliste und Stand."""

    def get(self, request: Request, pk: int) -> Response:
        """Liefert Aufgabe, Checkliste und den Stand des angemeldeten Nutzers.

        Args:
            request: Die Anfrage.
            pk: ID der Projektaufgabe.

        Returns:
            200 mit der Projektaufgabe; 404, wenn es sie nicht gibt.
        """
        projekt = get_object_or_404(Projektaufgabe, pk=pk)
        stand = projekt_stand(projekt, angemeldeter_nutzer(request))
        return Response(_projekt_antwort(projekt, stand))


class ProjektPunktView(APIView):
    """`PUT /api/projekte/<id>/punkte/<punkt_id>/`: Checklisten-Punkt abhaken."""

    def put(self, request: Request, pk: int, punkt_id: int) -> Response:
        """Hakt den Punkt ab oder nimmt den Haken zurück.

        Args:
            request: Anfrage mit `{"erledigt": true|false}`.
            pk: ID der Projektaufgabe.
            punkt_id: ID des Checklisten-Punkts.

        Returns:
            200 mit der aktualisierten Projektaufgabe; 400 bei ungültiger Eingabe;
            404, wenn es Projekt oder Punkt (in diesem Projekt) nicht gibt.
        """
        punkt = get_object_or_404(
            ProjektPunkt.objects.select_related("projektaufgabe"), pk=punkt_id, projektaufgabe_id=pk
        )
        eingabe = ProjektPunktSetzenSerializer(data=request.data)
        eingabe.is_valid(raise_exception=True)
        stand = setze_projektpunkt(
            punkt, angemeldeter_nutzer(request), eingabe.validated_data["erledigt"]
        )
        return Response(_projekt_antwort(punkt.projektaufgabe, stand))
