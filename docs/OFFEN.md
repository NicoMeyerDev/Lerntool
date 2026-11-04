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

## 2026-11-03 – Vor dem Deployment: Speicherort des Login-Tokens bestätigen

- **Stand:** Die API nutzt DRF-Token (siehe ENTSCHEIDUNGEN, B2). Das Frontend (B3) muss das Token speichern. Üblich und einfach ist `localStorage`; das Token wäre dann bei einer XSS-Lücke im Frontend auslesbar. React schützt standardmäßig vor XSS, und die App rendert keine fremden Inhalte – das Risiko ist für eine Ein-Personen-App klein, aber nicht null.
- **Warum nicht allein entschieden:** Betrifft Sicherheit (CLAUDE.md §7). Lokal ist es unkritisch; die Frage wird wichtig, sobald die App im Internet läuft.
- **Ebenfalls vor dem Deployment bestätigen:**
  - DRF-Tokens laufen nie ab; es gibt eines pro Nutzer, ungültig erst durch Logout. Für einen Nutzer vertretbar, im Internet eher eine Laufzeit (z. B. Neu-Login nach einigen Tagen) einbauen.
  - Die Login-Bremse zählt pro IP-Adresse. Hinter dem Proxy von Render sähe sie nur die Proxy-IP; dann `NUM_PROXIES` in den DRF-Einstellungen setzen und einen gemeinsamen Cache verwenden.
- **Vorschlag:** Für die Entwicklung `localStorage` verwenden. Vor dem Deployment entscheiden, ob das so bleibt oder auf Session-Cookies (HttpOnly, CSRF) umgestellt wird – das ist einfacher, wenn Frontend und Backend unter derselben Domain laufen.

## 2026-11-04 – Englisch (C4): Was bedeutet „Einstieg ab SAP 2122“?

- **Problem:** Der Backlog-Eintrag C4 nennt „Einstieg ab SAP 2122“. Im Projekt (Lernplan, Curriculum, Code) steht nirgends, was das ist (Kurs, Lehrbuch, Prüfungsnummer, Niveau?).
- **Annahme bis zur Klärung:** Die Gliederung beginnt bei Niveau A1 und führt in Phase 1 bis A2, so wie der Lernplan „Basisniveau“ nennt (siehe `docs/CURRICULUM_ENGLISCH.md`). Das ist eine Planungsannahme, kein Fakt.
- **Bitte klären:** Was „SAP 2122“ ist und ab welcher Stelle (Niveau, Thema) du einsteigen willst. Danach werden Phase 1 angepasst oder Themenfelder übersprungen.

## 2026-11-04 – Englisch (C4): Audio für Hörübungen

- **Problem:** Die App soll Hören üben (ohne Mikrofon). Eigene Aufnahmen gibt es nicht, fremde Audios dürfen nicht kopiert werden.
- **Optionen:** (a) Hörtexte verlinken (z. B. British Council LearnEnglish), (b) Sprachausgabe im Browser, (c) eigene Aufnahmen. Jede Option hat Folgen für Lizenz, Kosten oder Qualität.
- **Warum nicht allein entschieden:** Betrifft Kosten und Rechte (CLAUDE.md §7). Die Entscheidung wird vor der Ausarbeitung der Hörlektionen gebraucht, nicht für die Gliederung.

## Erledigt

### 2026-11-03 – Dateinamen wichen von der CLAUDE.md ab

- **Problem:** Die Steuerdatei hieß `Claude.md` statt `CLAUDE.md` (Claude Code lädt unter Linux nur `CLAUDE.md` automatisch), der Lernplan `docs/LERPLAN.md` statt `docs/LERNPLAN.md`.
- **Lösung (auf Wunsch des Nutzers):** Beide Dateien mit `git mv` umbenannt, Inhalt unverändert.

### 2026-11-03 – Git-Schutz-Hook lief auf diesem Rechner nicht

- **Problem:** `.claude/settings.json` startete die Hooks mit `python ...`. Auf dem Linux-Rechner gibt es nur `python3`. Der Hook-Aufruf schlug fehl und blockierte nichts.
- **Lösung (auf Wunsch des Nutzers):** Die Hooks rufen jetzt `python3` auf. Getestet: Ein Befehl mit Push auf `main` wird blockiert.
- **Hinweis für Windows:** Dort gibt es `python3` oft nicht (oder nur den Microsoft-Store-Platzhalter). Dann laufen die Hooks unter Windows nicht. Bei A3 geprüft: siehe offener Punkt „Hooks und Windows-Anleitung auf Windows ungeprüft“.
