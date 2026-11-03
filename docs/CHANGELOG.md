# Changelog

## 2026-11-03

- B1 Datenmodell: neue Django-App `lernen` mit Thema, Phase, Lektion, Abschnitt, Quelle, Quiz, Test, Frage, Antwort, Projektaufgabe und Fortschritt. Datenbank-Regeln (Constraints) sichern u. a. höchstens eine richtige Antwort je Frage und die Testdauer von höchstens 30 Minuten. 37 Modell-Tests in `backend/tests/test_lernen_modelle.py`.
- A3 README: Schritt-für-Schritt-Anleitung für Windows (Python, Node.js, PostgreSQL, Backend, Frontend), Fehlerbehebung und Kurzfassung für Linux und macOS. `.gitattributes` erzwingt LF-Zeilenenden. Neue offene Punkte in `docs/OFFEN.md`: Windows-Anleitung ist nicht auf Windows ausprobiert, Dateinamen `Claude.md` und `LERPLAN.md`.
- Steuerdatei `Claude.md` in `CLAUDE.md` und `docs/LERPLAN.md` in `docs/LERNPLAN.md` umbenannt (auf Wunsch des Nutzers).
- A2 Frontend-Gerüst: React, Vite, TypeScript, Tailwind und PWA in `/frontend`, API-Anbindung über Vite-Proxy, Startseite mit Systemstatus, Vitest-Tests, ESLint und Prettier. Die CI prüft jetzt auch die Prettier-Formatierung. Offener Punkt zum Git-Schutz-Hook in `docs/OFFEN.md`.
- A1 Backend-Gerüst: Django und Django REST Framework, Konfiguration über Umgebungsvariablen (`config/env.py`), PostgreSQL-Anbindung, Health-Endpunkt `GET /api/health/`, pytest-Tests, Anpassung der CI.
- Fix: Hooks in `.claude/settings.json` starten mit `python3` statt `python` (Git-Schutz und Lint-Prüfung liefen unter Linux nicht). Reviewer-Agent-Datei von `reviewer.md.` in `reviewer.md` umbenannt.
