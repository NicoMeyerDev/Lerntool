"""Tests für die Betriebs-Einstellungen (CORS, Render-Hostname, HTTPS)."""

import importlib
from types import ModuleType

import pytest

from config import settings


@pytest.fixture
def neu_laden(monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    """Lädt `config.settings` mit gesetzten Umgebungsvariablen neu und stellt danach zurück."""

    def laden(**variablen: str) -> ModuleType:
        for name in (
            "RENDER_EXTERNAL_HOSTNAME",
            "DJANGO_CORS_ORIGINS",
            "DJANGO_HTTPS_ERZWINGEN",
            "DJANGO_ALLOWED_HOSTS",
        ):
            monkeypatch.delenv(name, raising=False)
        for name, wert in variablen.items():
            monkeypatch.setenv(name, wert)
        return importlib.reload(settings)

    yield laden
    monkeypatch.undo()
    importlib.reload(settings)


def test_standard_ohne_betriebswerte(neu_laden) -> None:  # type: ignore[no-untyped-def]
    """Ohne Betriebsvariablen: kein CORS, kein HTTPS-Zwang, nur lokale Hosts."""
    s = neu_laden()
    assert s.CORS_ALLOWED_ORIGINS == []
    assert s.ALLOWED_HOSTS == ["localhost", "127.0.0.1"]
    assert not hasattr(s, "SECURE_SSL_REDIRECT")


def test_render_hostname_wird_erlaubt(neu_laden) -> None:  # type: ignore[no-untyped-def]
    """Der von Render gesetzte Hostname kommt in ALLOWED_HOSTS."""
    s = neu_laden(RENDER_EXTERNAL_HOSTNAME="lerntool-api.onrender.com")
    assert "lerntool-api.onrender.com" in s.ALLOWED_HOSTS


def test_cors_origins_aus_variable(neu_laden) -> None:  # type: ignore[no-untyped-def]
    """Kommagetrennte Frontend-Adressen werden als Liste übernommen."""
    s = neu_laden(DJANGO_CORS_ORIGINS="https://a.onrender.com, https://b.example")
    assert s.CORS_ALLOWED_ORIGINS == ["https://a.onrender.com", "https://b.example"]


def test_https_schalter(neu_laden) -> None:  # type: ignore[no-untyped-def]
    """Mit DJANGO_HTTPS_ERZWINGEN gelten Umleitung, sichere Cookies und Health-Ausnahme."""
    s = neu_laden(DJANGO_HTTPS_ERZWINGEN="True")
    assert s.SECURE_SSL_REDIRECT is True
    assert s.SESSION_COOKIE_SECURE is True
    assert s.CSRF_COOKIE_SECURE is True
    assert s.SECURE_PROXY_SSL_HEADER == ("HTTP_X_FORWARDED_PROTO", "https")
    assert s.SECURE_HSTS_SECONDS == 3600
    assert s.SECURE_REDIRECT_EXEMPT == [r"^api/health/$"]
