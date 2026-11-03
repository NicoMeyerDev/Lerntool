# Backlog

Regeln: Immer die oberste offene Aufgabe aus „Jetzt“ bearbeiten. Aufgaben aus „Später“ nicht anfangen. Ablauf und Stopp-Regeln stehen in der CLAUDE.md. Jede Aufgabe ist erst fertig, wenn die Kriterien erfüllt sind.

## Jetzt

### A. Fundament
- [ ] **A1 Backend-Gerüst:** Django und Django REST Framework in `/backend`. Einstellungen über Umgebungsvariablen, Datenbank über `DATABASE_URL` (PostgreSQL), `.env.example` ohne echte Werte, Endpunkt `/api/health/`, `requirements.txt` mit ruff, mypy, pytest. Fertig, wenn: alle Befehle aus CLAUDE.md Abschnitt 9 laufen, die CI ist grün, ein Test für `/api/health/` existiert.
- [ ] **A2 Frontend-Gerüst:** React, Vite, TypeScript (strict), Tailwind, vite-plugin-pwa in `/frontend`. Dunkles Theme mit Design-Tokens, Startseite ruft `/api/health/` auf. Fertig, wenn: `npm run lint`, `npm test`, `npm run build` laufen und die CI grün ist.
- [ ] **A3 README:** Lokales Setup unter Windows (Backend, Frontend, Datenbank), Befehle, Ordnerstruktur. Fertig, wenn: ein Neuling die App nach der Anleitung starten kann.

### B. Lernfluss
- [ ] **B1 Datenmodell:** Thema, Phase, Lektion, Abschnitt, Quiz, Frage, Antwort, Test, Projektaufgabe, Fortschritt. Migrationen und Tests.
- [ ] **B2 API:** Inhalte lesen, Quiz abgeben und auswerten, Fortschritt speichern. Einfacher Zugang für einen Nutzer (Entscheidung in `/docs/ENTSCHEIDUNGEN.md` festhalten).
- [ ] **B3 Lektions- und Quiz-Ansicht:** Lektion lesen, Quiz nach jedem Abschnitt, Ergebnis mit kurzer Auswertung.
- [ ] **B4 Test und Projekt:** Test mit 30-Minuten-Timer nach jedem Themenfeld, Projektaufgabe mit Checkliste und Auswertung.
- [ ] **B5 Dashboard:** Fortschrittsbalken, Statistiken, XP und Level, Abzeichen, Meilensteine.
- [ ] **B6 Wochen- und Tagesplan:** Feste Blöcke (Vormittag Theorie, Nachmittag Praxis), 5 Tage pro Woche, Freitag Test und Wochenauswertung.

### C. Inhalte (jede Aufgabe mit `quellenpruefer`)
- [ ] **C1 Curriculum Laravel, Gliederung:** 6 Phasen (PHP-Basics, Laravel-Kern, API und Auth, Docker, Kubernetes, AWS/Cloudflare), jede in Abschnitte, Themenfelder und ein Projekt zerlegt. Abschlussprojekt ist die Garmin-Auswertung. Frontend ausgeklammert.
- [ ] **C2 Phase 1 PHP-Basics von Grund auf:** Variablen und Typen, Operatoren, Kontrollstrukturen, Funktionen, Arrays, Klassen und Objekte, Namespaces und Composer, Fehlerbehandlung. Kein Vorwissen voraussetzen. Python-Vergleich nur als Eselsbrücke. Quelle: php.net.
- [ ] **C3 Phase 2 Laravel-Kern:** Routing, Controller, Eloquent, Migrationen, Validierung, Tests. Quelle: laravel.com/docs, Version prüfen.
- [ ] **C4 Englisch, Gliederung:** Einstieg ab SAP 2122. Pfad Alltag und Ausland, dann Fachenglisch IT, am Ende optional Sprachtest. Nur Lesen, Hören und Schreiben, kein Mikrofon.

## Später (nicht anfangen)
- [ ] **E1 AI Engineering, Gliederung und Phase 1:** Themen 1-3 aus `/docs/LERNPLAN.md`, Block 5, in Abschnitte und Quizze zerlegen. Mit `quellenpruefer`, aktuelle Doku zwingend.
- [ ] **D1 Wiederholung Backend:** Themen 1-10 der Backend-Roadmap in Abschnitte und Quizze zerlegen. Priorität: Auth, Datenbanken, API, Testing, CI/CD, Monitoring.
- [ ] **D2 Wiederholung DevSecOps:** Themen 1-10 der DevSecOps-Roadmap. Praktische Labs (Kali, Metasploitable, Juice Shop) nur als Theorie und Quiz, Labs nur in der eigenen Umgebung.
- [ ] **D3 Konzept-Vergleiche Django und Laravel:** Auth, Datenbanken, API, Testing, Docker, CI/CD als gemeinsame Lektionen mit zwei Umsetzungen.
- [ ] KI-Analyse der Schwächen und adaptive Aufgaben
- [ ] Offline-Modus
- [ ] Deployment auf Render (braucht Zugangsdaten vom Nutzer)
- [ ] Phasen 3 bis 6 Laravel ausarbeiten
- [ ] Kursinhalte Python, Django, DevSecOps
- [ ] Docker, Automation, AI Engineering, Cyber Security
- [ ] Russisch, mehrere Nutzer
