"""Gemeinsame Fixtures für alle Backend-Tests."""

from collections.abc import Iterator

import pytest
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from tests.fabrik import Inhalte, baue_inhalte


@pytest.fixture(autouse=True)
def leerer_cache() -> None:
    """Leert den Cache vor jedem Test, damit die Login-Bremse nicht nachwirkt."""
    cache.clear()


@pytest.fixture(autouse=True)
def schnelles_passwort_hashing() -> Iterator[None]:
    """Nutzt in Tests einen schnellen Passwort-Hasher (Empfehlung der Django-Doku).

    Nur für Tests: In Betrieb bleibt der sichere Standard-Hasher aktiv.
    """
    with override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"]):
        yield


@pytest.fixture
def inhalte(db: None) -> Inhalte:
    """Legt eine vollständige, minimale Inhaltskette an."""
    return baue_inhalte()


@pytest.fixture
def nutzer(db: None) -> User:
    """Legt einen Nutzer an."""
    return User.objects.create_user(username="lernender", password="geheim-123")


@pytest.fixture
def client_angemeldet(nutzer: User) -> APIClient:
    """API-Client, der sich mit dem Token von `nutzer` ausweist."""
    token = Token.objects.create(user=nutzer)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client
