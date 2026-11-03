# Entscheidungen

Format: Datum – Entscheidung – Grund – Alternativen.

## 2026-11-03 – A1 Backend-Gerüst

- **Django 5.2 (LTS)** – Langzeit-Support, stabile Basis. Alternative: Django 6.x (kürzerer Support).
- **Projektname `config`, erste App `core`** – übliche Konvention, trennt Projekteinstellungen von Fach-Apps. Alternative: Projektname `backend` (doppelt mit Ordnernamen).
- **Umgebungsvariablen mit `os.environ` + `python-dotenv`, Datenbank mit `dj-database-url`** – klein, typisiert, gut dokumentiert; `.env` wird nur lokal gelesen. Alternative: `django-environ` (mehr Funktionen, schlechtere Typisierung).
- **`DJANGO_SECRET_KEY` und `DATABASE_URL` sind Pflicht, kein Standardwert im Code** – keine versehentlich unsicheren Werte in Produktion. In der CI steht ein offensichtlicher Test-Schlüssel. Alternative: Standardschlüssel im Debug-Modus.
- **PostgreSQL-Treiber `psycopg` 3 (binary)** – aktueller, von Django empfohlener Treiber. Alternative: `psycopg2`.
- **`/api/health/` prüft auch die Datenbank (`SELECT 1`), Antwort 503 bei Fehler** – Health-Check zeigt so echte Betriebsbereitschaft. Die Logik liegt im Service `core/services.py`. Endpunkt braucht keine Anmeldung. Alternative: nur statisches „ok“.
- **Werkzeug-Konfiguration in `backend/pyproject.toml`**: ruff (inkl. Docstring-Regeln, Google-Stil), mypy `strict` mit Django- und DRF-Plugin, pytest-django. Alternative: getrennte `setup.cfg`/`mypy.ini`.
- **Versionen in `requirements.txt` fest gepinnt** – reproduzierbare CI. Alternative: Bereiche (`>=`).
- **Lokale Datenbank für Tests: PostgreSQL 16 per Docker** – gleiche Version wie in der CI. Anleitung folgt mit A3.
- **Env-Helfer in `config/env.py` statt in `settings.py`** – so ohne Seiteneffekte importier- und testbar (`tests/test_env.py`). Alternative: Helfer in `settings.py` belassen.
- **Kein Django-Admin** – nicht im Backlog verlangt, spart Angriffsfläche. Kann später bei Bedarf ergänzt werden. Alternative: Admin unter `/admin/` aus der Standardvorlage behalten.

## 2026-11-03 – A2 Frontend-Gerüst

- **Projekt mit `npm create vite` (Vorlage `react-ts`) erzeugt** – offizieller Weg, wenig eigener Code. Beispiel-Dateien der Vorlage entfernt.
- **ESLint (flat config, `typescript-eslint` strictTypeChecked) statt des Vorlagen-Linters oxlint** – der Lint-Hook ruft `eslint` auf, und `typescript-eslint` verbietet `any` typgeprüft. Alternative: oxlint (schneller, weniger typgeprüfte Regeln).
- **TypeScript 6.0 statt 7.0** – `typescript-eslint` unterstützt derzeit nur TypeScript < 6.1. `strict` ist in den tsconfig-Dateien ausdrücklich gesetzt. Alternative: TypeScript 7 ohne typgeprüftes ESLint.
- **Tailwind CSS 4 mit `@tailwindcss/vite`, Design-Tokens per `@theme` in `src/index.css`** – Tokens erzeugen direkt Tailwind-Klassen (`bg-surface`, `text-accent-cyan`). Alternative: eigene CSS-Variablen plus `tailwind.config`.
- **API-Aufruf mit `fetch` und TanStack Query** – Stack laut CLAUDE.md, keine weitere Bibliothek. Antworten werden per Type Guard geprüft, `503` wird als Zustand angezeigt, nicht als Fehler.
- **React Router noch nicht eingebunden** – es gibt nur eine Seite; kommt mit der ersten weiteren Ansicht (B3). Alternative: jetzt schon einbinden (ungenutzter Code).
- **API-Adresse über `VITE_API_URL`, lokal leer mit Vite-Proxy `/api` → `http://localhost:8000`** – keine CORS-Einstellungen im Backend nötig. Für das Deployment muss das später entschieden werden.
- **PWA: `vite-plugin-pwa` mit `autoUpdate`, ein SVG-Icon** – genügt für A2. PNG-Icons (192/512 px) für ältere Geräte folgen bei Bedarf. Offline-Modus steht unter „Später“.
- **Prettier für `npm run format`, Tests mit Vitest + jsdom + Testing Library** – Standard im Vite-Umfeld.
- **`npm audit`: 0 Lücken in Laufzeit-Abhängigkeiten, 21 mittlere/niedrige nur in Build-Werkzeugen (workbox-Kette von `vite-plugin-pwa`)** – betreffen nicht den ausgelieferten Code. Kein `npm audit fix --force`, weil es Major-Versionen tauschen würde.

## 2026-11-03 – A3 README mit Windows-Anleitung

- **Windows-Anleitung mit PowerShell und dem Python install manager (`py install 3.12`, `py -V:3.12 -m venv`)** – laut docs.python.org der aktuelle Weg; der alte `py`-Launcher ist seit Python 3.14 veraltet. Alternative: Installer einer festen Python-Version.
- **PostgreSQL unter Windows: EDB-Installer mit pgAdmin als Hauptweg, Docker Desktop als Alternative** – kein WSL/Docker nötig, Benutzer und Datenbank per SQL im pgAdmin-Query-Tool. Benutzer bekommt `CREATEDB`, weil pytest eine Test-Datenbank anlegt.
- **`.gitattributes` mit `* text=auto eol=lf`** – Git für Windows wandelt sonst beim Auschecken in CRLF um, und `npm run format:check` (Prettier erwartet LF) schlägt fehl. Bestehende Dateien sind bereits LF, nichts ändert sich. Alternative: Prettier `endOfLine: auto` (löst das Problem nur für Prettier).
- **Geprüft:** Linux-Kurzfassung in einem frischen Klon nachgestellt (migrate, check, 18 Backend- und 15 Frontend-Tests grün). Die Windows-Schritte sind gegen die offizielle Doku (docs.python.org, postgresql.org) geprüft, aber nicht auf einem Windows-Rechner ausprobiert.
