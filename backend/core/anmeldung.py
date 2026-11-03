"""Hilfsfunktionen rund um den angemeldeten Nutzer."""

from django.contrib.auth.models import User
from rest_framework.exceptions import NotAuthenticated
from rest_framework.request import Request


def angemeldeter_nutzer(request: Request) -> User:
    """Liefert den angemeldeten Nutzer einer Anfrage.

    Args:
        request: Die Anfrage.

    Returns:
        Den angemeldeten Nutzer.

    Raises:
        NotAuthenticated: Wenn niemand angemeldet ist (DRF antwortet dann mit 401).
    """
    nutzer = request.user
    if not isinstance(nutzer, User):
        raise NotAuthenticated()
    return nutzer
