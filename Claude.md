# Lern-App – Agent Harness & Master-Kontext

Diese Datei steuert Claude Code in diesem Projekt. Jede Sitzung hält sich strikt an diese Vorgaben. Der Nutzer ist Lernender und trifft keine technischen Entscheidungen: Die Regeln in dieser Datei ersetzen Rückfragen.

## 1. Projekt & Architektur
*   **Ziel:** Persönliche Lern-App (PC und Handy als PWA): Lektionen, Quizze, Tests, Projekte, Auswertung, Fortschritt, Abzeichen. Erste Themen: PHP/Laravel und Englisch.
*   **Backend:** Python, Django, Django REST Framework, PostgreSQL. Hosting auf Render.
*   **Frontend:** React, Vite, TypeScript (strict), Tailwind CSS, React Router, TanStack Query, vite-plugin-pwa. Tests mit Vitest und Testing Library.
*   **Architektur:** Frontend und Backend strikt getrennt, Kommunikation nur über die REST-API. Geschäftslogik im Backend in Services, nicht in Views. Das Frontend enthält keine Geschäftslogik, nur Darstellung und Bedienung.
*   **Verzeichnisse:** `/backend` (inkl. `/backend/tests`), `/frontend`, `/docs`, `/.claude/agents`

## 2. Sprache & Dokumentation
*   Alles auf Deutsch: Docstrings, Kommentare, Doku, Commit-Messages, UI-Texte.
*   Backend: deutsche Docstrings für jede Funktion, Klasse, jedes Modul (Zweck, Parameter, Rückgabe). Frontend: deutsche TSDoc-Kommentare für Komponenten und Funktionen.
*   Bezeichner im Code dürfen englisch sein, wenn das der Konvention entspricht.
*   README (Setup, Befehle, Struktur) und `/docs` müssen immer zum Code passen.

## 3. Coding-Richtlinien
*   Sauberer, lesbarer, stark typisierter Code. Python mit Typannotationen, TypeScript ohne `any`.
*   Einfache Funktionen und Komposition statt tiefer Vererbung. Framework-Konventionen haben Vorrang.
*   Fehler explizit abfangen und loggen. Keine leeren `except`- oder `catch`-Blöcke.
*   Keine Secrets im Code. Zugangsdaten nur über Umgebungsvariablen, `.env` nie committen.
*   Baue nur, was im Backlog steht. Keine ungefragten Features.

## 4. Frontend-Design
*   Dunkler, moderner Gaming-Look: dunkler Hintergrund, kräftige Akzentfarben (z. B. Cyan und Violett), klare Typografie.
*   Motivation sichtbar machen: Fortschrittsbalken, Statistiken, XP und Level, Abzeichen, Meilensteine, Wochen- und Tagesplan mit festen Blöcken (Vormittag Theorie, Nachmittag Praxis).
*   Mobile-first, große Touch-Flächen, gut lesbare Kontraste, Animationen dezent und abschaltbar (`prefers-reduced-motion`).
*   Wiederverwendbare Komponenten, Farben und Abstände zentral als Design-Tokens.

## 5. Lerninhalte
*   Nur offizielle Dokumentation und vertrauenswürdige Quellen. Kein Reddit, keine Foren, keine Blogs ohne Autorität.
*   Jede Lektion enthält Quellenangaben mit Link. Nichts erfinden. Nicht belegbare Aussagen als unsicher kennzeichnen oder weglassen.
*   Texte in eigenen Worten formulieren, keine wörtlichen Übernahmen größerer Passagen.
*   Erklärstil: kurz, bildlich, einfache Sprache, mit Beispielen. Grundlagen verstehen und sicher anwenden.
*   Ablauf: Quiz nach jedem Abschnitt, Test (max. 30 Min.) nach jedem Themenfeld, kleines Projekt nach einem Themenblock, kurze Auswertung.
*   Quizfragen eindeutig, richtige Antwort belegbar.
*   Lies vor jeder Arbeit an Lerninhalten `/docs/LERNPLAN.md`. Sie legt Themen, Reihenfolge, Lernstil und Ausgangsstand fest. Weiche nicht davon ab, ohne es in `/docs/ENTSCHEIDUNGEN.md` zu begründen.

## 6. Agenten-Team & Ablauf
*   **Hauptsession = Orchestrator und Builder.** Sie schreibt den Code und ruft die Subagenten ausdrücklich beim Namen auf.
*   `reviewer`: prüft Architektur, Docstrings, Sicherheit, Tests (nur Leserechte).
*   `quellenpruefer`: prüft Lerninhalte auf Quellen und fachliche Richtigkeit (nur Leserechte, Websuche).
*   `git-pfleger`: Branches, Commits, Push von Feature-Branches, Pull Requests, README und Doku.

**Ablauf pro Backlog-Aufgabe (`/docs/BACKLOG.md`, oberste offene Aufgabe zuerst):**
1. `git-pfleger`: Feature-Branch anlegen.
2. Bauen, mit Tests. Linter, Typprüfung und Tests lokal ausführen.
3. Enthält die Aufgabe Lerninhalte: `quellenpruefer` aufrufen.
4. `reviewer` aufrufen.
5. Bei „ÜBERARBEITEN“ oder „NACHBESSERN“: Punkte abarbeiten, erneut prüfen lassen. Maximal 3 Runden, danach Stopp (siehe Abschnitt 7).
6. `git-pfleger`: README und Doku aktualisieren, committen, Branch pushen, Pull Request öffnen.
7. Merge nach `main` nur, wenn CI grün ist und `reviewer` sowie (bei Lerninhalten) `quellenpruefer` freigegeben haben.
8. Aufgabe im Backlog abhaken, nächste Aufgabe.

## 7. Selbstständiges Arbeiten
*   **Entscheide selbst** bei allem, was nicht in Abschnitt 1 festgelegt ist: Wähle die einfachste, konventionelle Lösung und halte sie in `/docs/ENTSCHEIDUNGEN.md` fest (Datum, Entscheidung, Grund, Alternativen).
*   **Stoppe und melde dich** (Eintrag in `/docs/OFFEN.md`, dann nächste unabhängige Aufgabe), wenn:
    *   eine Änderung Sicherheit, Kosten (API-Aufrufe, Hosting) oder das Löschen von Daten betrifft,
    *   der Stack aus Abschnitt 1 geändert werden müsste,
    *   nach 3 Review-Runden keine Freigabe vorliegt,
    *   Tests nach 3 Korrekturversuchen weiter fehlschlagen,
    *   eine Anforderung widersprüchlich oder unklar ist und eine falsche Annahme teuer wäre.
*   Nie raten bei Fakten in Lerninhalten. Im Zweifel weglassen und in `/docs/OFFEN.md` eintragen.
*   Arbeite in kleinen Aufgaben. Überspringe nie Tests, Linter oder Review, um schneller fertig zu werden.

## 8. Git-Workflow
*   **Nie direkt auf `main` committen oder pushen. Nie force-pushen. Nie `--no-verify`.**
*   Jede Arbeit auf einem Branch: `feature/<kurzbeschreibung>`, `fix/<...>`, `docs/<...>`.
*   Commit-Messages auf Deutsch mit Präfix: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`. Beispiel: `feat: Quiz-Auswertung nach Abschnitt ergänzt`.
*   Kleine, in sich schlüssige Commits. Vor dem Commit `git status` und `git diff` prüfen, keine Secrets oder `.env`.
*   Push nur, wenn Linter, Typprüfung und Tests lokal grün sind.
*   `main` bekommt Änderungen nur per Pull Request mit grüner CI und den Freigaben aus Abschnitt 6.
*   Kann eine Änderung diese Bedingungen nicht erfüllen, nicht umgehen, sondern in `/docs/OFFEN.md` melden.

## 9. Terminal-Befehle
*   **Backend starten:** `python manage.py runserver`
*   **Backend-Tests:** `pytest`
*   **Backend Linter, Format, Typen:** `ruff check .`, `ruff format .`, `mypy .`
*   **Backend validieren:** `python manage.py check`
*   **Frontend starten:** `npm run dev` (im Ordner `/frontend`)
*   **Frontend-Tests:** `npm test`
*   **Frontend Linter, Format:** `npm run lint`, `npm run format`
*   **Frontend-Build:** `npm run build`

## 10. Abschluss-Checkliste (mechanisch prüfen)
1. [ ] Baut das Projekt fehlerfrei (Backend und Frontend)?
2. [ ] Linter, Typprüfung und Tests grün?
3. [ ] Neue Funktionen durch Tests abgedeckt?
4. [ ] Deutsche Docstrings und TSDoc vorhanden?
5. [ ] README und `/docs` aktuell?
6. [ ] Neue Lerninhalte mit Quellen und vom `quellenpruefer` freigegeben?
7. [ ] `reviewer` hat „FREIGABE“ gegeben?
8. [ ] Entscheidungen in `/docs/ENTSCHEIDUNGEN.md`, offene Punkte in `/docs/OFFEN.md`?
