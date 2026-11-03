# Offene Punkte

Punkte, die eine Entscheidung oder Aktion des Nutzers brauchen.

## Erledigt

### 2026-11-03 – Git-Schutz-Hook lief auf diesem Rechner nicht

- **Problem:** `.claude/settings.json` startete die Hooks mit `python ...`. Auf dem Linux-Rechner gibt es nur `python3`. Der Hook-Aufruf schlug fehl und blockierte nichts.
- **Lösung (auf Wunsch des Nutzers):** Die Hooks rufen jetzt `python3` auf. Getestet: Ein Befehl mit Push auf `main` wird blockiert.
- **Hinweis für Windows:** Dort gibt es `python3` oft nicht (oder nur den Microsoft-Store-Platzhalter). Dann laufen die Hooks unter Windows nicht. Bei der Windows-Anleitung (A3) prüfen und ggf. melden.
