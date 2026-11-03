"""API-Views der Lern-App. Nur Ein- und Ausgabe; die Logik liegt in `lernen.services`."""

from dataclasses import asdict

from django.db.models import Prefetch, QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.anmeldung import angemeldeter_nutzer
from lernen.models import Abschnitt, Fortschritt, Frage, Lektion, Phase, Quiz, Thema
from lernen.serializers import (
    FortschrittSerializer,
    LektionDetailSerializer,
    QuizAbgabeSerializer,
    QuizSerializer,
    ThemaDetailSerializer,
    ThemaSerializer,
)
from lernen.services import UngueltigeAbgabe, markiere_abschnitt_gelesen, werte_quiz_aus


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
