# Changelog

## 2026-11-03

- A1 Backend-Gerüst: Django und Django REST Framework, Konfiguration über Umgebungsvariablen (`config/env.py`), PostgreSQL-Anbindung, Health-Endpunkt `GET /api/health/`, pytest-Tests, Anpassung der CI.
- Fix: Hooks in `.claude/settings.json` starten mit `python3` statt `python` (Git-Schutz und Lint-Prüfung liefen unter Linux nicht). Reviewer-Agent-Datei von `reviewer.md.` in `reviewer.md` umbenannt.
