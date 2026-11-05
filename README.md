# Lerntool

Persönliche Lern-App für PC und Handy (PWA) mit Lektionen, Quizzen, Tests, Projekten, Fortschritt, XP und Abzeichen. Erste Themen: PHP/Laravel, Englisch, AI Engineering sowie Wiederholungen zu Backend und DevSecOps.

- **Backend:** Python, Django, Django REST Framework, PostgreSQL (`/backend`)
- **Frontend:** React, Vite, TypeScript, Tailwind CSS, PWA (`/frontend`)
- Beide sprechen nur über die REST-API miteinander. Die Lerninhalte liegen als YAML-Dateien in `backend/inhalte`.

## Inhaltsverzeichnis

1. [Schnellstart](#schnellstart)
2. [Einrichtung unter Windows](#einrichtung-unter-windows)
3. [App starten und bedienen](#app-starten-und-bedienen)
4. [Befehle](#befehle)
5. [API](#api)
6. [Projektstruktur](#projektstruktur)
7. [Deployment auf Render](#deployment-auf-render)
8. [Fehlerbehebung](#fehlerbehebung)
9. [Weitere Dokumentation](#weitere-dokumentation)

## Schnellstart

Für Linux und macOS (Python 3.12, Node.js 22 und Docker vorausgesetzt):

```bash
# Datenbank
docker run -d --name lerntool-postgres -e POSTGRES_USER=lerntool -e POSTGRES_PASSWORD=lerntool -e POSTGRES_DB=lerntool -p 5432:5432 postgres:16

# Backend
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                 # Werte eintragen, siehe "Einstellungen"
python manage.py migrate
python manage.py import_inhalte      # Lerninhalte laden, gefahrlos wiederholbar
python manage.py createsuperuser     # eigenen Zugang anlegen
python manage.py runserver

# Frontend (zweites Terminal)
cd frontend
npm ci
npm run dev                          # http://localhost:5173
```

## Einrichtung unter Windows

Alle Befehle laufen in **PowerShell**. Zeilen mit `#` sind Erklärungen.

### 1. Programme installieren

| Programm | Woher | Prüfen mit |
| --- | --- | --- |
| Git | https://git-scm.com/downloads/win | `git --version` |
| Python 3.12 | Python install manager von https://www.python.org/downloads/, dann `py install 3.12` | `py -V:3.12 --version` |
| Node.js 22 (LTS) | https://nodejs.org/en/download | `node --version` |
| PostgreSQL 16 | siehe Schritt 2 | – |

Danach PowerShell neu öffnen und das Projekt herunterladen:

```powershell
cd $HOME
git clone https://github.com/NicoMeyerDev/Lerntool.git
cd Lerntool
```

### 2. Datenbank

Wähle eine Variante. In beiden lautet die Verbindung `postgres://lerntool:lerntool@localhost:5432/lerntool` (einfaches Passwort, nur für lokale Entwicklung).

**Variante A: Installer.** PostgreSQL 16 von https://www.postgresql.org/download/windows/ installieren (Standardoptionen, Port `5432`, Passwort für `postgres` merken). In *pgAdmin* über *Tools → Query Tool* **nacheinander einzeln** ausführen:

```sql
CREATE ROLE lerntool LOGIN PASSWORD 'lerntool' CREATEDB;
```

```sql
CREATE DATABASE lerntool OWNER lerntool;
```

`CREATEDB` braucht der Benutzer, weil die Tests eine eigene Test-Datenbank anlegen.

**Variante B: Docker Desktop.**

```powershell
docker run -d --name lerntool-postgres -e POSTGRES_USER=lerntool -e POSTGRES_PASSWORD=lerntool -e POSTGRES_DB=lerntool -p 5432:5432 postgres:16
```

Später wieder starten: `docker start lerntool-postgres`.

### 3. Backend einrichten

```powershell
cd $HOME\Lerntool\backend
py -V:3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Meldet `Activate.ps1` einen Fehler wegen der Ausführungsrichtlinie: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` und erneut aktivieren.

**Einstellungen:** Einen Schlüssel erzeugen mit `python -c "import secrets; print(secrets.token_urlsafe(50))"` und `backend\.env` ausfüllen:

```
DJANGO_SECRET_KEY=<erzeugter Schlüssel>
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://lerntool:lerntool@localhost:5432/lerntool
```

| Variable | Pflicht | Bedeutung |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | ja | geheimer Schlüssel, langer Zufallswert |
| `DATABASE_URL` | ja | `postgres://BENUTZER:PASSWORT@HOST:PORT/DATENBANK` |
| `DJANGO_DEBUG` | nein | `True` nur lokal, Standard `False` |
| `DJANGO_ALLOWED_HOSTS` | nein | kommagetrennte Hostnamen, Standard `localhost,127.0.0.1` |

Weitere Variablen für den Betrieb stehen in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md). Die Datei `.env` enthält Geheimnisse und wird nie committet.

**Tabellen, Inhalte, Zugang:**

```powershell
python manage.py migrate
python manage.py import_inhalte      # Lerninhalte laden, gefahrlos wiederholbar
python manage.py check
pytest
python manage.py createsuperuser     # einmalig: dein Zugang (die App hat genau einen Nutzer)
```

Passwort vergessen: `python manage.py changepassword <benutzername>`.

### 4. Frontend einrichten

In einem **zweiten** PowerShell-Fenster:

```powershell
cd $HOME\Lerntool\frontend
npm ci
npm test
```

Eine `.env` ist lokal nicht nötig: Der Entwicklungsserver leitet `/api` an `http://localhost:8000` weiter.

## App starten und bedienen

Es laufen zwei Fenster nebeneinander.

```powershell
# Fenster 1: Backend
cd $HOME\Lerntool\backend
.venv\Scripts\Activate.ps1
python manage.py runserver
```

```powershell
# Fenster 2: Frontend
cd $HOME\Lerntool\frontend
npm run dev
```

Dann **http://localhost:5173** öffnen und mit dem Nutzer aus `createsuperuser` anmelden. Beenden mit `Strg + C`.

**Bedienung:**
- Die Startseite zeigt Themen, Fortschritt, XP, Abzeichen und den Wochenplan. Ein Klick auf ein Thema öffnet die Lektionen.
- Eine Lektion zeigt einen Abschnitt pro Bildschirm. „Gelesen – weiter“ markiert ihn. Das Quiz wertet aus, sobald alle Fragen beantwortet sind.
- Pro Themenfeld gibt es einen Test mit Zeitlimit und pro Themenblock ein Projekt mit Checkliste.
- Der „Systemstatus“ unten auf der Startseite zeigt, ob Backend und Datenbank erreichbar sind.

## Befehle

| Zweck | Backend (Ordner `backend`) | Frontend (Ordner `frontend`) |
| --- | --- | --- |
| Starten | `python manage.py runserver` | `npm run dev` |
| Tests | `pytest` | `npm test` |
| Linter | `ruff check .` | `npm run lint` |
| Formatieren | `ruff format .` | `npm run format` |
| Typprüfung / Build | `mypy .` | `npm run build` |
| Validieren | `python manage.py check` | – |
| Datenbank migrieren | `python manage.py migrate` | – |
| Lerninhalte laden | `python manage.py import_inhalte` | – |

## API

Alle Endpunkte außer `health` und `login` brauchen den Header `Authorization: Token <token>`, sonst gibt es `401`.

| Endpunkt | Zweck |
| --- | --- |
| `GET /api/health/` | Zustand von API und Datenbank (`503`, wenn die Datenbank fehlt) |
| `POST /api/auth/login/` | Anmeldung, liefert den Token (höchstens 10 Versuche pro Minute) |
| `POST /api/auth/logout/` | Token ungültig machen |
| `GET /api/auth/ich/` | angemeldeter Nutzer |
| `GET /api/themen/`, `GET /api/themen/<slug>/` | Themen, mit Phasen, Lektionen und Projekten |
| `GET /api/lektionen/<id>/` | Lektion mit Abschnitten, Quellen, Quiz und Test |
| `GET /api/quizze/<id>/`, `POST …/abgabe/` | Quizfragen ohne Lösung, Auswertung |
| `GET /api/tests/<id>/`, `POST …/start/`, `POST …/abgabe/` | Test mit serverseitiger Uhr, Auswertung (`409` bei abgelaufener Zeit) |
| `GET /api/projekte/<id>/`, `PUT …/punkte/<punkt_id>/` | Projektaufgabe, Checklistenpunkt abhaken |
| `POST /api/abschnitte/<id>/gelesen/` | Abschnitt als gelesen markieren |
| `GET /api/fortschritt/`, `GET /api/dashboard/` | Fortschritt, XP, Level, Abzeichen, Meilensteine |
| `GET /api/wochenplan/?datum=JJJJ-MM-TT` | Wochen- und Tagesplan (Mo–So) |

## Projektstruktur

```
backend/
  config/       Django-Einstellungen, Umgebungsvariablen, URLs
  core/         Health-Check, Anmeldung, Verwaltungsbefehl anlegen_nutzer
  lernen/       Lerninhalte, Fortschritt, Dashboard, Wochenplan, Import
  inhalte/      Lerninhalte als YAML (Themen, Phasen, Lektionen)
  tests/        pytest-Tests
frontend/
  src/api/      API-Aufrufe und Prüfung der Antworten
  src/pages/    Seiten (Login, Start, Thema, Lektion, Test, Projekt, Plan)
  src/components/  wiederverwendbare Komponenten
docs/           Lernplan, Backlog, Entscheidungen, offene Punkte, Changelog, Deployment
.github/workflows/ci.yml   CI: Linter, Typen, Tests, Build
render.yaml     Blueprint für Render
```

## Deployment auf Render

`render.yaml` legt Datenbank, Backend und Frontend an. Schritt-für-Schritt-Anleitung, benötigte Angaben und Grenzen des kostenlosen Tarifs: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Fehlerbehebung

| Meldung | Lösung |
| --- | --- |
| `py`/`python` nicht gefunden oder Microsoft Store öffnet sich | Windows-Einstellungen → „App-Ausführungsaliase verwalten“ → „Python (default)“ einschalten, PowerShell neu öffnen |
| `Activate.ps1 … kann nicht geladen werden` | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `Umgebungsvariable … fehlt` | `backend\.env` fehlt oder ist unvollständig |
| `connection refused` (Port 5432) | PostgreSQL starten: Dienst „postgresql-x64-16“ oder `docker start lerntool-postgres` |
| `password authentication failed for user "lerntool"` | Benutzer anders angelegt als in `DATABASE_URL`, SQL aus Schritt 2 prüfen |
| `CREATE DATABASE cannot run inside a transaction block` | Die beiden SQL-Befehle einzeln ausführen |
| `permission denied to create database` beim Testen | in pgAdmin `ALTER ROLE lerntool CREATEDB;` |
| `npm` nicht gefunden | Node.js installieren, PowerShell neu öffnen |
| Startseite zeigt „Backend nicht erreichbar“ | Backend starten, Port 8000 muss frei sein |

## Weitere Dokumentation

- [docs/LERNPLAN.md](docs/LERNPLAN.md): Themen, Reihenfolge, Lernstil
- [docs/BACKLOG.md](docs/BACKLOG.md): Aufgaben und Stand
- [docs/ENTSCHEIDUNGEN.md](docs/ENTSCHEIDUNGEN.md) und [docs/OFFEN.md](docs/OFFEN.md): Entscheidungen und offene Punkte
- [docs/CHANGELOG.md](docs/CHANGELOG.md): Änderungen
- [CLAUDE.md](CLAUDE.md): Regeln für die Arbeit mit Claude Code
