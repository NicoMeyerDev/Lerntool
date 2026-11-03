# Offene Punkte

Punkte, die eine Entscheidung oder Aktion des Nutzers brauchen.

## 2026-11-03 – Git-Schutz-Hook läuft auf diesem Rechner nicht

- **Problem:** `.claude/settings.json` startet die Hooks mit `python ...`. Auf dem Linux-Rechner gibt es nur `python3`, kein `python`. Der Hook-Aufruf schlägt fehl und blockiert deshalb nichts: Der Schutz vor Commit/Push auf `main`, Force-Push und `--no-verify` ist aktuell wirkungslos (dasselbe gilt für den Lint-Hook).
- **Warum nicht selbst behoben:** Betrifft eine Sicherheitseinstellung (CLAUDE.md Abschnitt 7).
- **Vorschlag:** In `.claude/settings.json` `python3` statt `python` verwenden, oder systemweit `python-is-python3` installieren (`sudo apt install python-is-python3`). Unter Windows heißt der Befehl meist `python` oder `py` – die erste Variante wäre dort zu prüfen.
