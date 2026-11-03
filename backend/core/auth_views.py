"""Anmeldung per Token: Login, Logout und Abfrage des angemeldeten Nutzers."""

from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from core.anmeldung import angemeldeter_nutzer


class LoginView(ObtainAuthToken):
    """`POST /api/auth/login/`: Benutzername und Passwort gegen ein Token tauschen.

    Antwortet mit `{"token": "..."}` oder 400 bei falschen Zugangsdaten.
    Höchstens 10 Versuche pro Minute (Schutz gegen Durchprobieren von Passwörtern).
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"


class LogoutView(APIView):
    """`POST /api/auth/logout/`: Token des angemeldeten Nutzers ungültig machen."""

    def post(self, request: Request) -> Response:
        """Löscht das Token, sodass es nicht mehr verwendet werden kann.

        Args:
            request: Die angemeldete Anfrage.

        Returns:
            204 ohne Inhalt.
        """
        Token.objects.filter(user=angemeldeter_nutzer(request)).delete()
        return Response(status=204)


class IchView(APIView):
    """`GET /api/auth/ich/`: Daten des angemeldeten Nutzers."""

    def get(self, request: Request) -> Response:
        """Liefert ID und Benutzernamen des angemeldeten Nutzers.

        Args:
            request: Die angemeldete Anfrage.

        Returns:
            200 mit `{"id": ..., "benutzername": ...}`.
        """
        nutzer = angemeldeter_nutzer(request)
        return Response({"id": nutzer.pk, "benutzername": nutzer.get_username()})
