"""Tests für den Verwaltungsbefehl `anlegen_nutzer`."""

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError


def test_legt_nutzer_an(db: None, monkeypatch: pytest.MonkeyPatch) -> None:
    """Ohne Nutzer wird einer aus den Umgebungsvariablen angelegt."""
    monkeypatch.setenv("LERNTOOL_BENUTZER", "nico")
    monkeypatch.setenv("LERNTOOL_PASSWORT", "ein-langes-passwort-1")
    call_command("anlegen_nutzer")
    nutzer = User.objects.get(username="nico")
    assert nutzer.check_password("ein-langes-passwort-1")


def test_zweiter_aufruf_aendert_nichts(db: None, monkeypatch: pytest.MonkeyPatch) -> None:
    """Existiert schon ein Nutzer, bleibt Passwort und Bestand unverändert."""
    User.objects.create_user(username="alt", password="altes-passwort-1")
    monkeypatch.setenv("LERNTOOL_BENUTZER", "neu")
    monkeypatch.setenv("LERNTOOL_PASSWORT", "neues-passwort-1")
    call_command("anlegen_nutzer")
    assert list(User.objects.values_list("username", flat=True)) == ["alt"]
    assert User.objects.get(username="alt").check_password("altes-passwort-1")


def test_ohne_variablen_fehler(db: None, monkeypatch: pytest.MonkeyPatch) -> None:
    """Fehlen die Variablen und gibt es keinen Nutzer, bricht der Befehl ab."""
    monkeypatch.delenv("LERNTOOL_BENUTZER", raising=False)
    monkeypatch.delenv("LERNTOOL_PASSWORT", raising=False)
    with pytest.raises(CommandError):
        call_command("anlegen_nutzer")


@pytest.mark.parametrize(
    ("benutzer", "passwort"),
    [("nico", ""), ("", "ein-langes-passwort-1"), ("   ", "ein-langes-passwort-1")],
)
def test_unvollstaendige_angaben_fehler(
    db: None, monkeypatch: pytest.MonkeyPatch, benutzer: str, passwort: str
) -> None:
    """Fehlt Benutzer oder Passwort (oder besteht der Name nur aus Leerzeichen), gibt es Fehler."""
    monkeypatch.setenv("LERNTOOL_BENUTZER", benutzer)
    monkeypatch.setenv("LERNTOOL_PASSWORT", passwort)
    with pytest.raises(CommandError):
        call_command("anlegen_nutzer")
    assert not User.objects.exists()


@pytest.mark.parametrize("passwort", ["1234", "passwort", "12345678901234"])
def test_schwaches_passwort_abgelehnt(
    db: None, monkeypatch: pytest.MonkeyPatch, passwort: str
) -> None:
    """Zu kurze, häufige oder rein numerische Passwörter legen keinen Nutzer an."""
    monkeypatch.setenv("LERNTOOL_BENUTZER", "nico")
    monkeypatch.setenv("LERNTOOL_PASSWORT", passwort)
    with pytest.raises(CommandError):
        call_command("anlegen_nutzer")
    assert not User.objects.exists()
