"""API-Views der Kern-App."""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.services import datenbank_erreichbar


class HealthView(APIView):
    """Health-Check: meldet, ob die API läuft und die Datenbank erreichbar ist."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        """Liefert den Zustand von API und Datenbank.

        Args:
            request: Die eingehende Anfrage.

        Returns:
            200 mit `{"status": "ok", "datenbank": "ok"}`, wenn alles läuft,
            sonst 503 mit `{"status": "fehler", "datenbank": "nicht erreichbar"}`.
        """
        if datenbank_erreichbar():
            return Response({"status": "ok", "datenbank": "ok"})
        return Response(
            {"status": "fehler", "datenbank": "nicht erreichbar"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
