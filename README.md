# Lerntool

Lern-App mit Django-Backend (REST-API über Django REST Framework) und PostgreSQL. Das Frontend folgt später in `/frontend`.

## Struktur

```
backend/
  config/      Django-Konfiguration: settings.py, env.py (Umgebungsvariablen), urls.py
  core/        Health-Endpunkt (Views, Services, URLs)
  tests/       pytest-Tests
docs/          Backlog, Lernplan, Entscheidungen, offene Punkte, Changelog
.github/workflows/ci.yml   CI (Linter, Typen, Tests)
```

## Backend einrichten

Voraussetzungen: Python 3.12, PostgreSQL 16.

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # danach Werte eintragen
```

Variablen in `backend/.env` (nie committen):

| Variable | Pflicht | Bedeutung |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | ja | geheimer Schlüssel, eigener langer Zufallswert |
| `DATABASE_URL` | ja | `postgres://BENUTZER:PASSWORT@HOST:PORT/DATENBANK` |
| `DJANGO_DEBUG` | nein | `True` nur lokal |
| `DJANGO_ALLOWED_HOSTS` | nein | kommagetrennte Hostnamen |

PostgreSQL 16 lokal, z. B. per Docker:

```bash
docker run -d --name lerntool-postgres -e POSTGRES_USER=lerntool -e POSTGRES_PASSWORD=lerntool -e POSTGRES_DB=lerntool -p 5432:5432 postgres:16
```

Dazu passt `DATABASE_URL=postgres://lerntool:lerntool@localhost:5432/lerntool` (nur lokale Entwicklung).

Eine ausführliche Windows-Anleitung folgt mit Aufgabe A3.

## Befehle (im Ordner `backend`)

- Starten: `python manage.py runserver`
- Tests: `pytest`
- Linter, Format, Typen: `ruff check .`, `ruff format .`, `mypy .`
- Validieren: `python manage.py check`

## API

`GET /api/health/` liefert `200 {"status":"ok","datenbank":"ok"}`, bei nicht erreichbarer Datenbank `503`.
