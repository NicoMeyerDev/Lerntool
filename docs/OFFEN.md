# Offene Punkte

Punkte, die eine Entscheidung oder Aktion des Nutzers brauchen.

## 2026-11-03 – Git-Schutz-Hook blockiert zu viel („main“ irgendwo im Befehl)

- **Problem:** `.claude/hooks/git_schutz.py` blockiert jeden Bash-Befehl, der `git push` enthält und irgendwo das Wort `main` – auch wenn gar nicht auf `main` gepusht wird. Beispiel: `git push -u origin feature/x && gh pr create --base main` wird komplett abgelehnt. Ursache: Die Prüfung `\b(main|master)\b` läuft über den ganzen Befehl statt nur über den Push-Teil.
- **Folge:** Kein Sicherheitsrisiko (es wird eher zu viel blockiert), aber Agenten müssen Befehle aufteilen oder `--base main` weglassen.
- **Warum nicht selbst behoben:** Betrifft eine Sicherheitseinstellung (CLAUDE.md Abschnitt 7).
- **Vorschlag:** Den Befehl an `&&`, `||`, `;` und `|` in Teilbefehle zerlegen und `main`/`master` nur im Teilbefehl mit `git push` prüfen. Dazu Tests für den Hook ergänzen (z. B. „Push auf Feature-Branch + `--base main`“ erlaubt, `git push origin main` und `git push origin HEAD:main` blockiert).

## 2026-11-03 – Hooks und Windows-Anleitung auf Windows ungeprüft

- **Stand:** Laut [Python-Doku](https://docs.python.org/3/using/windows.html) bringt der Python install manager einen `python3`-Befehl mit, die Hooks sollten also auch unter Windows starten. Ausprobiert ist das nicht, ebenso wenig die übrigen Windows-Schritte im README (kein Windows-Rechner verfügbar).
- **Bitte beim ersten Einrichten unter Windows:** `python3 --version` prüfen und melden, wo die Anleitung hakt. Fehlt `python3`, muss für die Hooks eine plattformübergreifende Lösung her (Sicherheitseinstellung, daher nicht ohne Rücksprache).

## 2026-11-03 – Dateinamen weichen von der CLAUDE.md ab

- `Claude.md` heißt nicht `CLAUDE.md`. Unter Linux unterscheidet das Dateisystem Groß- und Kleinschreibung; Claude Code lädt standardmäßig `CLAUDE.md`. In dieser Sitzung wurde die Datei nicht automatisch geladen, sondern von Hand gelesen.
- `docs/LERPLAN.md` heißt nicht `docs/LERNPLAN.md`, wie die CLAUDE.md (Abschnitt 5) verlangt.
- **Warum nicht selbst behoben:** `Claude.md` ist die Steuerdatei des Projekts; Umbenennen ändert, wie jede Sitzung arbeitet. Vorschlag: beide Dateien umbenennen (`git mv Claude.md CLAUDE.md`, `git mv docs/LERPLAN.md docs/LERNPLAN.md`), gern als eigene kleine `docs/`-Aufgabe.

## Erledigt

### 2026-11-03 – Git-Schutz-Hook lief auf diesem Rechner nicht

- **Problem:** `.claude/settings.json` startete die Hooks mit `python ...`. Auf dem Linux-Rechner gibt es nur `python3`. Der Hook-Aufruf schlug fehl und blockierte nichts.
- **Lösung (auf Wunsch des Nutzers):** Die Hooks rufen jetzt `python3` auf. Getestet: Ein Befehl mit Push auf `main` wird blockiert.
- **Hinweis für Windows:** Dort gibt es `python3` oft nicht (oder nur den Microsoft-Store-Platzhalter). Dann laufen die Hooks unter Windows nicht. Bei A3 geprüft: siehe offener Punkt „Hooks und Windows-Anleitung auf Windows ungeprüft“.
