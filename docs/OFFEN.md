# Offene Punkte

Punkte, die eine Entscheidung oder Aktion des Nutzers brauchen.

## 2026-11-05 – Quizqualität: Überarbeitung Backend, PHP/Laravel, AI Engineering, Englisch

- **Stand:** Alle Themen sind überarbeitet bis auf die Quizzes der D3-CI-Lektion (nach Merge von PR #27).
- **Positionsrotation:** Die Rotation ist zyklisch und damit vorhersagbar. Mischen im Frontend wäre besser.
- **Vom `quellenpruefer` bestätigen lassen** (der `reviewer` konnte sie ohne Websuche nicht prüfen): Laravel 13.x mit PHP 8.3 als Mindestversion, Attribut `#[Fillable]`, Ausgabenlimit-Verhalten der Claude-API.

## 2026-11-05 – D3 Konzept-Vergleiche: Notizen

- **PHP-GitHub-Actions-Quelle fehlt:** Für die PHP/Laravel-Schritte in der CI-Lektion gibt es keine belegte offizielle Quelle. Die Schritte sind als ungeprüft gekennzeichnet und müssen nachgeprüft werden.
- **Laravel-Test-Datenbank:** Details zur Test-Datenbank in der Laravel-Doku nachschlagen und in der Testlektion prüfen.
- **Quizqualität:** Wie in Teil 3 ist die richtige Antwort oft die längste Option, Falschantworten sind teils schwach. Später gleich lang und plausibel formulieren.

## 2026-11-05 – D2 DevSecOps: Notizen zu Quellen und Quizqualität

Reine Notizen, keine Entscheidung des Lernenden nötig.

- **DSGVO-Quelle:** Die Quelle bei eur-lex.europa.eu konnte nicht abgerufen werden. Bitte im Browser prüfen, ob der Link stimmt und der Inhalt zur Lektion passt.
- **Quizqualität:** Wie in D1 Teil 3 ist die richtige Antwort oft die längste Option, die Falschantworten sind teils schwach. Später gleich lang und plausibel formulieren.
- **Review:** Runde 2 des `reviewer` war nur eine Nachprüfung der Änderungen.
- **NIST 64 Zeichen:** Die Obergrenze von 64 Zeichen bei Passwörtern ist laut NIST ein SHOULD, keine Pflicht.

## 2026-11-05 – D1 Teil 3: Notizen zu Quizqualität, Review und Datenbankverbindung

Reine Notizen, keine Entscheidung des Lernenden nötig.

- **Quizqualität:** In D1 Teil 3 ist die richtige Antwort oft die längste Option und häufig an Position 2 (ca. 30, 48 und 21 Prozent auf Position 1, 2 und 3). Das Frontend mischt noch nicht (Backlog). Später die Falschantworten plausibel und gleich lang formulieren.
- **Review-Umfang:** Der `reviewer` hat in Runde 2 nur 7 von 18 Dateien erneut gelesen; Runde 1 hat alle gelesen.
- **Datenbankverbindung:** Das Projekt nutzt `DATABASE_URL` mit `conn_max_age=600`; die Django-Doku rät für ASGI bzw. die Entwicklung zu anderen Einstellungen. Beim Deployment prüfen.

## 2026-11-04 – D1 Teil 2: Kleine Lücken in DevOps und Monitoring

Reine Notiz, keine Entscheidung des Lernenden nötig.

- **Prometheus-Metriktypen:** Stehen nicht auf der Overview-Seite und sind deshalb nicht in der Lektion. Später mit eigener Quelle ergänzen.
- **GitHub Actions, Secrets:** Optional die ergänzende Quelle „Using secrets in GitHub Actions“ (GitHub Docs) aufnehmen.

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

### 2026-11-04 – Antwortreihenfolge in älteren Inhalten

- **Problem:** In den Inhalten `php-laravel` (rund 78 Prozent), `ai-engineering` und `englisch` (je 100 Prozent) steht die richtige Antwort überwiegend an erster Stelle. Die App mischt die Antworten nicht, die Lösung ist so erratbar.
- **Lösung:** Die Reihenfolge der Antworten ist in `php-laravel`, `ai-engineering` und `englisch` verteilt (PR dieser Aufgabe, reine Umsortierung). Offen bleibt nur die Idee, im Frontend zu mischen; sie steht unter „Später“ im Backlog.

### 2026-11-04 – DRF 3.18 und Django 5.2

- **Problem:** Die Release-Notes von DRF 3.18.0 bestätigen Django 5.2 nicht ausdrücklich (sie nennen 6.1 und den Wegfall von 4.2, 5.0 und 5.1).
- **Plan:** Vor einem Versions-Update prüfen.
