# Offene Punkte

Punkte, die eine Entscheidung oder Aktion des Nutzers brauchen.

## 2026-11-04 – Englisch (C5): Lücken in Phase 1

Reine Notiz für die spätere Ausarbeitung (Backlog C6), keine Entscheidung des Lernenden nötig. Jeweils: Quelle suchen.

- **Hören (1.3.5 und Hörteil im Projekt Reiseplan):** Quelle suchen; setzt die Audio-Umsetzung voraus.
- **Reisen (1.4.1):** Bahn, Bus, Flug, Durchsagen. Belegte Erwachsenenquelle suchen.
- **Restaurant und Arzt (1.4.4):** Belegte Quelle suchen.
- **Texte überfliegen (1.5.5):** Belegte Quelle suchen.
- **„Would you mind“ (1.5.3):** Quelle suchen, die es für A2 zeigt (die Seite „Requests, offers and invitations“ nennt es nicht).
- **Wegbeschreibung (1.4.2):** Bisher nur ein LearnEnglish-Kids-PDF (Kinderniveau). Erwachsenenquelle suchen.
- **Rechtschreibung der -ing-Form:** Zweite unabhängige Quelle suchen; bisher als eigene Erklärung gekennzeichnet.

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

## Erledigt

### 2026-11-04 – Englisch (C4): Was bedeutet „Einstieg ab SAP 2122“?

- **Problem:** Der Backlog nannte „Einstieg ab SAP 2122“, im Projekt stand nirgends, was das ist.
- **Lösung (Antwort des Lernenden):** Gemeint ist das heutige Englisch des Lernenden, eingeordnet als A2. Die Gliederung beginnt bei 1.3; 1.1 und 1.2 sind optionale Wiederholung (siehe `docs/CURRICULUM_ENGLISCH.md` und `docs/ENTSCHEIDUNGEN.md`).

### 2026-11-03 – Dateinamen wichen von der CLAUDE.md ab

- **Problem:** Die Steuerdatei hieß `Claude.md` statt `CLAUDE.md` (Claude Code lädt unter Linux nur `CLAUDE.md` automatisch), der Lernplan `docs/LERPLAN.md` statt `docs/LERNPLAN.md`.
- **Lösung (auf Wunsch des Nutzers):** Beide Dateien mit `git mv` umbenannt, Inhalt unverändert.

### 2026-11-03 – Git-Schutz-Hook lief auf diesem Rechner nicht

- **Problem:** `.claude/settings.json` startete die Hooks mit `python ...`. Auf dem Linux-Rechner gibt es nur `python3`. Der Hook-Aufruf schlug fehl und blockierte nichts.
- **Lösung (auf Wunsch des Nutzers):** Die Hooks rufen jetzt `python3` auf. Getestet: Ein Befehl mit Push auf `main` wird blockiert.
- **Hinweis für Windows:** Dort gibt es `python3` oft nicht (oder nur den Microsoft-Store-Platzhalter). Dann laufen die Hooks unter Windows nicht. Bei A3 geprüft: siehe offener Punkt „Hooks und Windows-Anleitung auf Windows ungeprüft“.

### 2026-11-04 – Englisch (C4): Audio für Hörübungen

- **Problem:** Die App soll Hören üben (ohne Mikrofon). Eigene Aufnahmen gibt es nicht, fremde Audios dürfen nicht kopiert werden.
- **Lösung (Antwort des Lernenden):** Eigene Aufnahmen sind erlaubt, wenn sie gut verständlich sind. Wie sie erzeugt werden (echte Aufnahme oder Sprachausgabe), bleibt offen und wird erst bei der Ausarbeitung der Hörlektionen entschieden, ohne Kosten und mit sauberer Lizenz.

### 2026-11-04 – AI Engineering (E1): Echte API-Aufrufe und Kosten

- **Problem:** Offen war, ob ein API-Schlüssel angelegt und echte Aufrufe gemacht werden (Kosten, Sicherheit).
- **Lösung (Antwort des Lernenden):** Der Lernende möchte vorerst keinen API-Schlüssel anlegen. Phase 1 geht ohne Aufruf; Phasen mit echten Aufrufen bleiben bis zu einer neuen Entscheidung zurückgestellt.
