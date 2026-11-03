# Lerntool

Persönliche Lern-App für PC und Handy (PWA). Das Backend ist Django mit Django REST Framework und PostgreSQL in `/backend`. Das Frontend ist React, Vite, TypeScript, Tailwind und PWA in `/frontend`. Beide sprechen nur über die REST-API miteinander.

**Inhalt:** [Voraussetzungen](#1-voraussetzungen-windows) · [Datenbank](#2-datenbank-postgresql-16) · [Backend](#3-backend-einrichten) · [Frontend](#4-frontend-einrichten) · [App starten](#5-app-starten) · [Befehle](#befehle) · [Fehlerbehebung](#fehlerbehebung) · [Linux/macOS](#kurzfassung-für-linux-und-macos) · [Struktur](#ordnerstruktur)

---

## Einrichtung unter Windows (Schritt für Schritt)

Alle Befehle laufen in **PowerShell**. Öffne sie über das Startmenü (Eingabe „PowerShell“). Zeilen, die mit `#` beginnen, sind Erklärungen und werden nicht eingegeben.

### 1. Voraussetzungen (Windows)

Einmalig installieren:

| Programm | Woher | Prüfen mit |
| --- | --- | --- |
| **Git** | https://git-scm.com/downloads/win (Standardoptionen genügen) | `git --version` |
| **Python 3.12** | Python install manager von https://www.python.org/downloads/, danach in PowerShell `py install 3.12` | `py -V:3.12 --version` |
| **Node.js 22** | https://nodejs.org/en/download, Version 22 (LTS), Windows-Installer (.msi) | `node --version` (zeigt `v22.…`) |
| **PostgreSQL 16** | siehe Schritt 2 | – |

Nach jeder Installation PowerShell **schließen und neu öffnen**, damit die neuen Befehle gefunden werden.

Projekt herunterladen:

```powershell
cd $HOME
git clone https://github.com/NicoMeyerDev/Lerntool.git
cd Lerntool
```

### 2. Datenbank: PostgreSQL 16

Wähle **eine** der beiden Varianten.

**Variante A: Installer (empfohlen für Einsteiger)**

1. Installer von https://www.postgresql.org/download/windows/ herunterladen (angeboten von EDB), **Version 16** wählen.
2. Installation mit Standardoptionen. Merke dir das Passwort, das du für den Benutzer `postgres` vergibst. Port `5432` beibehalten. StackBuilder am Ende brauchst du nicht.
3. **pgAdmin** aus dem Startmenü öffnen, mit dem `postgres`-Passwort anmelden.
4. Links auf *Servers → PostgreSQL 16 → Databases → postgres* klicken, dann oben *Tools → Query Tool*.
5. Die zwei Befehle **nacheinander einzeln** ausführen (zusammen schlägt `CREATE DATABASE` fehl). Erst diesen Befehl einfügen und mit dem Play-Knopf (oder `F5`) ausführen:

   ```sql
   CREATE ROLE lerntool LOGIN PASSWORD 'lerntool' CREATEDB;
   ```

   Dann das Eingabefeld leeren, diesen Befehl einfügen und wieder ausführen:

   ```sql
   CREATE DATABASE lerntool OWNER lerntool;
   ```

   `CREATEDB` braucht der Benutzer, weil die Tests eine eigene Test-Datenbank anlegen.

**Variante B: Docker Desktop**

Wenn Docker Desktop schon läuft:

```powershell
docker run -d --name lerntool-postgres -e POSTGRES_USER=lerntool -e POSTGRES_PASSWORD=lerntool -e POSTGRES_DB=lerntool -p 5432:5432 postgres:16
```

Später wieder starten: `docker start lerntool-postgres`.

In beiden Varianten lautet die Verbindung:
`postgres://lerntool:lerntool@localhost:5432/lerntool`
(Das einfache Passwort ist nur für die lokale Entwicklung gedacht.)

### 3. Backend einrichten

```powershell
cd $HOME\Lerntool\backend

# Virtuelle Umgebung mit Python 3.12 anlegen und aktivieren
py -V:3.12 -m venv .venv
.venv\Scripts\Activate.ps1

# Abhängigkeiten installieren
python -m pip install -r requirements.txt

# Einstellungen anlegen
Copy-Item .env.example .env
```

Meldet `Activate.ps1` einen Fehler wegen „Ausführungsrichtlinie“ bzw. „execution policy“, einmalig ausführen und dann erneut aktivieren:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Nach dem Aktivieren steht `(.venv)` vor der Eingabezeile. Ab hier heißt der Befehl einfach `python`.

**Geheimen Schlüssel erzeugen:**

```powershell
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

**`backend\.env` bearbeiten** (z. B. `notepad .env`) und ausfüllen:

```
DJANGO_SECRET_KEY=<hier die Ausgabe von eben einfügen>
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://lerntool:lerntool@localhost:5432/lerntool
```

| Variable | Pflicht | Bedeutung |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | ja | geheimer Schlüssel, eigener langer Zufallswert |
| `DATABASE_URL` | ja | `postgres://BENUTZER:PASSWORT@HOST:PORT/DATENBANK` |
| `DJANGO_DEBUG` | nein | `True` nur lokal, Standard `False` |
| `DJANGO_ALLOWED_HOSTS` | nein | kommagetrennte Hostnamen, Standard `localhost,127.0.0.1` |

Die Datei `.env` enthält Geheimnisse und wird **nie committet** (steht in `.gitignore`).

**Datenbanktabellen anlegen und prüfen:**

```powershell
python manage.py migrate
python manage.py check
pytest
```

`check` meldet „no issues“, `pytest` meldet alle Tests als `passed`.

### 4. Frontend einrichten

In einem **zweiten** PowerShell-Fenster:

```powershell
cd $HOME\Lerntool\frontend
npm ci
```

Eine `.env` ist lokal nicht nötig. Der Entwicklungsserver leitet alle Aufrufe an `/api` automatisch an das Backend auf `http://localhost:8000` weiter. Nur wenn das Backend woanders läuft: `Copy-Item .env.example .env` und dort `VITE_API_URL` setzen.

Prüfen:

```powershell
npm test
```

### 5. App starten

Es laufen immer **zwei Fenster** nebeneinander.

Fenster 1 (Backend):

```powershell
cd $HOME\Lerntool\backend
.venv\Scripts\Activate.ps1
python manage.py runserver
```

Fenster 2 (Frontend):

```powershell
cd $HOME\Lerntool\frontend
npm run dev
```

Dann im Browser **http://localhost:5173** öffnen. Die Startseite zeigt unter „Systemstatus“:
- grüner Punkt „Backend und Datenbank erreichbar“: alles läuft,
- roter Punkt „Backend nicht erreichbar“: Fenster 1 prüfen,
- roter Punkt „Backend erreichbar, Datenbank nicht“: PostgreSQL prüfen (Schritt 2).

Beenden mit `Strg + C` im jeweiligen Fenster.

---

## Befehle

**Backend** (im Ordner `backend`, virtuelle Umgebung aktiviert):

| Zweck | Befehl |
| --- | --- |
| Starten | `python manage.py runserver` |
| Tests | `pytest` |
| Linter | `ruff check .` |
| Formatieren | `ruff format .` |
| Typprüfung | `mypy .` |
| Validieren | `python manage.py check` |
| Datenbank migrieren | `python manage.py migrate` |

**Frontend** (im Ordner `frontend`):

| Zweck | Befehl |
| --- | --- |
| Starten | `npm run dev` |
| Tests | `npm test` |
| Linter | `npm run lint` |
| Formatieren / prüfen | `npm run format` / `npm run format:check` |
| Build | `npm run build` |

## API

`GET /api/health/` liefert `200 {"status":"ok","datenbank":"ok"}`, bei nicht erreichbarer Datenbank `503 {"status":"fehler","datenbank":"nicht erreichbar"}`.

## Fehlerbehebung

| Meldung | Lösung |
| --- | --- |
| `py` oder `python` wird nicht gefunden bzw. öffnet den Microsoft Store | Windows-Einstellungen → „App-Ausführungsaliase verwalten“: Alias „Python (default)“ einschalten. PowerShell neu öffnen. |
| `Activate.ps1 … kann nicht geladen werden` | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` (siehe Schritt 3) |
| `ImproperlyConfigured: Umgebungsvariable … fehlt` | `backend\.env` fehlt oder ist unvollständig (Schritt 3). |
| `connection refused` / `Verbindung abgelehnt` (Port 5432) | PostgreSQL läuft nicht. Installer-Variante: in „Dienste“ den PostgreSQL-Dienst (z. B. „postgresql-x64-16“) starten. Docker-Variante: `docker start lerntool-postgres`. |
| `password authentication failed for user "lerntool"` | Benutzer anders angelegt als in `DATABASE_URL`. SQL aus Schritt 2 prüfen. |
| `CREATE DATABASE cannot run inside a transaction block` | Beide SQL-Befehle wurden zusammen ausgeführt. `CREATE DATABASE …` allein noch einmal ausführen (Schritt 2). |
| `permission denied to create database` beim Testen | Dem Benutzer fehlt `CREATEDB`: in pgAdmin `ALTER ROLE lerntool CREATEDB;` |
| `npm` wird nicht gefunden | Node.js installieren und PowerShell neu öffnen. |
| Startseite zeigt „Backend nicht erreichbar“ | Backend in Fenster 1 starten, Port 8000 muss frei sein. |

## Kurzfassung für Linux und macOS

```bash
# Datenbank (Docker)
docker run -d --name lerntool-postgres -e POSTGRES_USER=lerntool -e POSTGRES_PASSWORD=lerntool -e POSTGRES_DB=lerntool -p 5432:5432 postgres:16

# Backend
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # Werte wie in Schritt 3 eintragen
python manage.py migrate
python manage.py runserver

# Frontend (zweites Terminal)
cd frontend
npm ci
npm run dev                   # http://localhost:5173
```

## Ordnerstruktur

```
backend/
  config/          Django-Konfiguration: settings.py, env.py (Umgebungsvariablen), urls.py
  core/            Health-Endpunkt (Views, Services, URLs)
  tests/           pytest-Tests
  manage.py        Django-Verwaltungsbefehle
  requirements.txt Python-Abhängigkeiten
  pyproject.toml   Einstellungen für ruff, mypy, pytest
  .env.example     Vorlage für backend/.env
frontend/
  src/main.tsx     Einstiegspunkt
  src/App.tsx      Startseite
  src/index.css    Design-Tokens und Grundstile
  src/api/         API-Aufrufe ans Backend
  src/components/  React-Komponenten
  src/test/        Test-Setup (Vitest)
  public/          statische Dateien, PWA-Icon
  vite.config.ts   Vite, Proxy, PWA, Tests
  eslint.config.js ESLint
  package.json     Node-Abhängigkeiten und npm-Skripte
  .env.example     Vorlage für frontend/.env
docs/          Backlog, Lernplan, Entscheidungen, offene Punkte, Changelog
.claude/       Claude-Code-Agenten und Hooks
.github/workflows/ci.yml   CI (Backend: Linter, Typen, Tests; Frontend: Lint, Prettier, Tests, Build)
```

## Hinweis für Claude Code unter Windows

Die Hooks in `.claude/settings.json` starten mit `python3`. Laut [Python-Doku zu Windows](https://docs.python.org/3/using/windows.html) bringt der Python install manager einen `python3`-Befehl mit (gedacht als Auffanglösung). Auf einem Windows-Rechner ausprobiert ist das noch nicht. Prüfen mit `python3 --version`; fehlt der Befehl, laufen die Hooks nicht – siehe `docs/OFFEN.md`.
