"""Tests für die Hilfsfunktionen in `config/env.py`."""

import pytest
from django.core.exceptions import ImproperlyConfigured

from config.env import env_bool, env_list, env_required

NAME = "LERNTOOL_TESTVARIABLE"


@pytest.mark.parametrize(
    ("wert", "erwartet"),
    [("1", True), ("true", True), (" TRUE ", True), ("on", True), ("off", False), ("0", False)],
)
def test_env_bool_wertet_text_aus(
    monkeypatch: pytest.MonkeyPatch, wert: str, erwartet: bool
) -> None:
    """Typische Schreibweisen werden korrekt als Wahrheitswert gelesen."""
    monkeypatch.setenv(NAME, wert)

    assert env_bool(NAME) is erwartet


@pytest.mark.parametrize("default", [True, False])
def test_env_bool_nutzt_standard_wenn_nicht_gesetzt(
    monkeypatch: pytest.MonkeyPatch, default: bool
) -> None:
    """Ohne gesetzte Variable kommt der Standardwert zurück."""
    monkeypatch.delenv(NAME, raising=False)

    assert env_bool(NAME, default=default) is default


def test_env_list_entfernt_leerzeichen_und_leere_eintraege(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Leerzeichen werden abgeschnitten, leere Einträge fallen weg."""
    monkeypatch.setenv(NAME, " a.de , ,b.de,, ")

    assert env_list(NAME) == ["a.de", "b.de"]


def test_env_list_nutzt_standard_wenn_nicht_gesetzt(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ohne gesetzte Variable wird der Standardwert zerlegt."""
    monkeypatch.delenv(NAME, raising=False)

    assert env_list(NAME, default="localhost,127.0.0.1") == ["localhost", "127.0.0.1"]


def test_env_required_liefert_gesetzten_wert(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ein gesetzter Wert wird ohne Leerzeichen am Rand zurückgegeben."""
    monkeypatch.setenv(NAME, " geheim ")

    assert env_required(NAME) == "geheim"


@pytest.mark.parametrize("wert", [None, "", "   "])
def test_env_required_meldet_fehlende_oder_leere_variable(
    monkeypatch: pytest.MonkeyPatch, wert: str | None
) -> None:
    """Fehlt die Variable oder ist sie leer, wird ImproperlyConfigured ausgelöst."""
    if wert is None:
        monkeypatch.delenv(NAME, raising=False)
    else:
        monkeypatch.setenv(NAME, wert)

    with pytest.raises(ImproperlyConfigured, match=NAME):
        env_required(NAME)
