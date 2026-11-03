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

## 2026-11-03 – B1 Datenmodell

- **Neue App `lernen`** für alle Lerninhalte und den Fortschritt; `core` bleibt für technische Endpunkte. Alternative: eine App je Bereich (Inhalte, Quiz, Fortschritt) – für den Umfang zu kleinteilig.
- **Hierarchie: Thema → Phase → Lektion → Abschnitt.** Eine Lektion entspricht einem *Themenfeld* aus CLAUDE.md Abschnitt 5 (z. B. „Arrays“ in Phase 1 PHP-Basics). Alternative: eigenes Modell „Themenfeld“ zwischen Phase und Lektion – zusätzliche Ebene ohne Bedarf.
- **Quiz 1:1 Abschnitt, Test 1:1 Lektion, Projektaufgabe n:1 Phase** – bildet „Quiz nach jedem Abschnitt, Test nach jedem Themenfeld, Projekt je Phase“ (CLAUDE.md §5, Backlog C1) direkt ab.
- **Zusätzliches Modell `Quelle` (Titel, URL) je Lektion** – CLAUDE.md §5 verlangt Quellenangaben mit Link in jeder Lektion; als eigene Tabelle prüfbar und mehrfach möglich. Alternative: Freitext-Feld (nicht prüfbar).
- **`Frage` gehört über zwei optionale Fremdschlüssel zu genau einem Quiz *oder* Test** (CheckConstraint). Alternative: generische Relation (ContentType) – schwerer zu prüfen und abzufragen.
- **Antworten: höchstens eine richtige je Frage per Datenbank-Regel** (bedingter UniqueConstraint), weil Quizfragen eindeutig sein müssen. „Mindestens eine richtige“ lässt sich nicht als einfache Datenbank-Regel ausdrücken; das prüft später der Import der Inhalte (C-Aufgaben). Nur Einfachauswahl; weitere Fragetypen bei Bedarf.
- **Test-Zeitlimit 1–30 Minuten**, Standard 30, als Validator und CheckConstraint.
- **`Fortschritt` als eine Tabelle mit vier optionalen Zielen (Abschnitt, Quiz, Test, Projektaufgabe)**, genau eines gesetzt, ein Eintrag je Nutzer und Ziel, Punkte nur mit Maximum. Verweist auf Djangos Standard-Nutzer (`AUTH_USER_MODEL`), damit B2 („einfacher Zugang für einen Nutzer“) und später mehrere Nutzer ohne Umbau möglich sind. Alternative: je Ziel eine eigene Fortschrittstabelle (vier fast gleiche Modelle). Einzelne Versuche (Historie) sind nicht Teil von B1.
- **Datenbank-Regeln NULL-sicher formulieren:** SQL-CHECKs gelten bei NULL als erfüllt; deshalb prüft `fortschritt_punkte_gueltig` `max_punkte` ausdrücklich auf NOT NULL (durch einen Test aufgefallen).
- **Eindeutigkeit mit optionalen Feldern:** Bei `Frage` (Quiz/Test) und `Fortschritt` (vier Ziele) greifen die UniqueConstraints nur, wenn das Feld gesetzt ist – PostgreSQL behandelt NULL-Werte als verschieden. Das ist gewollt (z. B. Position 1 im Quiz und im Test zugleich) und getestet.
- **Nicht per Datenbank erzwingbar, sondern beim Import der Inhalte (C-Aufgaben) zu prüfen:** jede Lektion hat mindestens eine Quelle, jede Frage genau eine richtige Antwort.
- **Mehrere Projektaufgaben je Phase erlaubt** (C1 nennt „ein Projekt“) – kein Mehraufwand und kein Umbau nötig, falls eine Phase zwei kleine Projekte braucht.
- **URL-Prüfung der Quellen nur per Validierung (`full_clean`), nicht in der Datenbank** – Import (C) und API (B2) müssen vor dem Speichern validieren. Offen für B2: wann gilt ein Abschnitt als erledigt (gelesen oder Quiz bestanden)?
- **Inhalt von Abschnitten und Projektaufgaben als Markdown-Text.** Darstellung folgt in B3.
- **Migrationen sind von den Docstring-Regeln (ruff `D`, `E501`) ausgenommen** – von Django erzeugter Code.
- **Kein Django-Admin** (siehe A1). Inhalte kommen in den C-Aufgaben per Import.

## 2026-11-03 – B2 API

- **Zugang für einen Nutzer: DRF-Token-Anmeldung** (`rest_framework.authtoken`). `POST /api/auth/login/` tauscht Benutzername und Passwort gegen ein Token, das das Frontend als `Authorization: Token …` mitschickt. Der Nutzer wird mit `python manage.py createsuperuser` angelegt (kein Registrieren). Grund: eingebaut in DRF, funktioniert auch, wenn Frontend und Backend später auf verschiedenen Domains laufen, keine CSRF-/Cookie-Einstellungen nötig. Alternativen: Session-Cookies mit CSRF (sicherer gegen Token-Diebstahl per XSS, aber bei getrennten Domains aufwendiger), JWT (zusätzliche Bibliothek, für einen Nutzer überdimensioniert). Sicherheitsfrage vor dem Deployment siehe `docs/OFFEN.md`.
- **Standard: jede API braucht Anmeldung** (`IsAuthenticated`), Ausnahmen nur `/api/health/` und `/api/auth/login/`. So kann ein neuer Endpunkt nicht versehentlich offen sein.
- **Login-Bremse: 10 Versuche pro Minute** (`ScopedRateThrottle`), gegen das Durchprobieren von Passwörtern. Zählt im lokalen Cache-Speicher; bei mehreren Server-Prozessen (Deployment) wäre ein gemeinsamer Cache nötig.
- **Logout löscht das Token** – danach ist es ungültig.
- **Quiz-Serializer verraten keine Lösung:** `ist_richtig` und `erklaerung` erscheinen erst in der Auswertung nach der Abgabe. Durch einen Test abgesichert.
- **Quiz-Abgabe als Liste `{"frage", "antwort"}`**, nicht als Objekt mit Frage-IDs als Schlüssel (JSON-Schlüssel wären Texte). Unbeantwortete Fragen zählen als falsch; fremde Fragen/Antworten, doppelte Fragen und leere Quizze → 400.
- **Gespeichert wird der Bestwert** je Nutzer und Quiz (Fortschritt soll nicht sinken). Ändert sich die Fragenzahl des Quiz, ersetzt die neue Abgabe den alten Wert. Einzelne Versuche werden nicht gespeichert (bei Bedarf später für die Schwächenanalyse).
- **Wann ist ein Abschnitt erledigt? Wenn der Nutzer ihn als gelesen markiert** (`POST /api/abschnitte/<id>/gelesen/`). Das Quiz-Ergebnis steht getrennt im Fortschritt. Grund: einfach, und Lesen ohne bestandenes Quiz bleibt sichtbar (Hinweis auf Wiederholung). Alternative: erledigt erst bei bestandenem Quiz (braucht eine Bestehensgrenze, die es noch nicht gibt).
- **Tests** (`TEST`-Modell) bekommen Lesen/Abgabe erst mit B4 (Timer); die Auswertungslogik ist so gebaut, dass sie dort wiederverwendet werden kann. **Für B4 zu entscheiden:** Eine leere Abgabe zeigt alle Lösungen – beim Quiz gewollt (Lernen), beim Test mit Timer ggf. erst nach Ablauf oder nur einmal.
- **Logik in `lernen/services.py`, Views nur Ein-/Ausgabe** (CLAUDE.md §1). Abfragen mit `prefetch_related`, damit eine Lektion mit vielen Abschnitten in wenigen Datenbankabfragen lädt (Test prüft ≤ 6).
- **Tests nutzen einen schnellen Passwort-Hasher** (`MD5PasswordHasher`, nur in `tests/conftest.py`), wie die Django-Doku empfiehlt; im Betrieb bleibt der sichere Standard. Testlaufzeit 35 s → 2 s.

## 2026-11-03 – B3 Lektions- und Quiz-Ansicht

- **React Router (`react-router`, Paket ab v7 ohne `-dom`)** für Seiten und Links: `/login`, `/`, `/themen/:slug`, `/lektionen/:id`. Geschützte Seiten leiten ohne Anmeldung auf `/login` um. Alternative: eigener Mini-Router (unüblich, mehr Code).
- **zod prüft jede API-Antwort zur Laufzeit** (`src/api/schemas.ts`); die TypeScript-Typen werden daraus abgeleitet. Grund: `strict` ohne `any` – ohne Prüfung wäre `response.json()` ein ungeprüfter Typ-Cast. Alternative: Typen von Hand plus Cast (keine echte Sicherheit).
- **Markdown mit `react-markdown`, `skipHtml`** – rohes HTML aus Lerntexten wird nicht ausgeführt (Schutz vor eingeschleustem Code). Links öffnen sich mit `rel="noopener noreferrer"` in neuem Tab. Alternative: `marked` + `dangerouslySetInnerHTML` (braucht zusätzlich einen HTML-Säuberer).
- **Token im `localStorage`** – bleibt nach Neuladen erhalten. Risiko bei XSS ist bekannt und in `docs/OFFEN.md` für das Deployment vermerkt. Antwortet die API mit 401, löscht das Frontend das Token und zeigt den Login.
- **Ein Abschnitt pro Bildschirm, Position in der URL (`?abschnitt=n`)** – kurze Lerneinheiten, Zurück-Taste und Neuladen funktionieren. Der Knopf „Gelesen – weiter“ markiert den Abschnitt als gelesen (B2-Entscheidung) und blättert weiter; der Fortschrittsbalken zeigt gelesene Abschnitte.
- **Quiz-Abgabe erst, wenn alle Fragen beantwortet sind** – vermeidet, dass ein versehentlicher Klick alle Lösungen zeigt. Danach: Punkte, Bestwert, richtige und eigene Antwort markiert, Erklärung bei falschen Antworten, „Nochmal versuchen“.
- **Neue Abhängigkeiten:** `react-router`, `zod`, `react-markdown`; für Tests `@testing-library/user-event` (realistische Klicks und Eingaben).
- **Geprüft im echten Browser** (Chrome headless, 420 px breit): Login, Themenübersicht, Lektion mit Codeblock, Quiz-Abgabe und Auswertung. Testdaten danach gelöscht.
- **Nach dem Review ergänzt:** Quellen-Links nur mit `http:`/`https:` (sonst nur Text, Schutz falls ungeprüfte Daten in die Datenbank gelangen); „nicht gefunden“ nur bei Status 404, sonst „Laden fehlgeschlagen“; ungültige Lektions-IDs lösen keine Anfrage aus; Rücklinks, Logo und „Abmelden“ mit mindestens 48 px Höhe; Tests für Fehlerfälle (Abgabe, „gelesen“, Quiz laden, letzter Abschnitt).
- **Kontraste nach WCAG gemessen:** alle Textfarben auf `bg`/`surface` mindestens 6:1 (AA verlangt 4,5:1), z. B. `text-muted` auf `surface` 6,9:1, Cyan auf `bg` 10,7:1.
- **„Stark – alles richtig!“ entscheidet das Frontend aus `punkte === max_punkte`** – reine Darstellung. Kommt eine Bestehensgrenze, liefert das Backend die Bewertung.

## 2026-11-03 – B4 Test und Projekt

- **Zeitlimit läuft auf dem Server** (`TestVersuch` mit Startzeit). `POST /api/tests/<id>/start/` startet den Versuch oder setzt den laufenden fort und liefert die Restzeit; das Frontend zählt nur von diesem Wert herunter und gibt bei 0 automatisch ab. Grund: Die Uhr des Geräts und das Neuladen der Seite dürfen das Limit nicht umgehen. Je Nutzer und Test höchstens ein laufender Versuch (bedingter UniqueConstraint). Alternative: Zeit nur im Frontend (leicht zu umgehen).
- **Kulanz 30 Sekunden** nach Ablauf (Netzwerk, automatische Abgabe). Danach: 409, nichts wird gespeichert, der Versuch ist beendet. Ein nie abgegebener, abgelaufener Versuch wird beim nächsten Start durch einen neuen ersetzt.
- **Lösungen erst nach der Abgabe** (Klärung der offenen B2-Frage): Ohne laufenden Versuch gibt es keine Auswertung (409). Jede Abgabe beendet den Versuch, ein weiterer Versuch braucht einen neuen Start. Eine ungültige Abgabe (400) beendet ihn nicht. Bekannte Eigenschaft: Wer neu startet, sieht die Lösungen des vorigen Versuchs – wie beim Quiz, für eine persönliche Lern-App akzeptabel.
- **`GET /api/tests/<id>/` liefert die Fragen auch ohne Start** (ohne Lösung). Die Zeitbegrenzung gilt für die Abgabe; das Frontend zeigt die Fragen erst nach dem Start. Alternative: Fragen erst beim Start ausliefern (mehr Aufwand, kaum Nutzen).
- **Bestwert wie beim Quiz** (Fortschritt je Nutzer und Test); die Auswertungslogik ist mit dem Quiz gemeinsam (`_werte_aus`), ebenso die Fragen-Darstellung im Frontend (`FragenListe`).
- **Bei Neuladen gehen die gewählten Antworten verloren**, die Uhr läuft weiter. Der Hinweis vor dem Start sagt das. Alternative: Antworten zwischenspeichern (nicht im Backlog).
- **Projekt-Checkliste als eigene Modelle** (`ProjektPunkt`, `ProjektPunktErledigt`). Das Projekt gilt als erledigt, wenn alle Punkte abgehakt sind; dann entsteht ein Fortschritt „n von n“. Wird ein Haken zurückgenommen, entfällt dieser Fortschritt wieder (abgeleitete Daten). Ein Projekt ohne Punkte ist nie abgeschlossen. Die „Auswertung“ ist die Rückmeldung nach Anzahl erledigter Punkte, keine Note. Alternative: Selbstbewertung mit Freitext (nicht gefordert).
- **Keine Eingabemöglichkeit für Checklisten-Punkte bis zum Inhaltsimport** (C-Aufgaben), da es keinen Django-Admin gibt (A1). Bis dahin sind sie nur über Tests und die Shell anlegbar.
- **Neue Endpunkte:** `GET /api/tests/<id>/`, `POST …/start/`, `POST …/abgabe/`, `GET /api/projekte/<id>/`, `PUT /api/projekte/<id>/punkte/<punkt_id>/`.

## 2026-11-03 – B5 Dashboard

- **Alles wird aus dem vorhandenen Fortschritt berechnet** (`lernen/dashboard.py`, `GET /api/dashboard/`), keine eigene Tabelle für XP oder Abzeichen. Grund: Es kann nie von den echten Ergebnissen abweichen, und Regeländerungen wirken sofort rückwirkend. Alternative: gespeicherte XP/Abzeichen mit Vergabezeitpunkt (nötig erst, wenn „erreicht am“ oder Serien gefragt sind).
- **XP-Regeln (Konstanten im Modul):** Abschnitt gelesen 10 XP, Quiz 5 XP je richtiger Frage (Bestwert), Test 10 XP je richtiger Frage (Bestwert), Projekt 50 XP. Tests zählen doppelt, weil sie unter Zeitdruck stehen. **Level:** alle 100 XP eins höher, Start bei Level 1. Einfach und verständlich; Zahlen sind Startwerte und lassen sich später anpassen.
- **Abzeichen** (einmalig): Erster Schritt, Volltreffer (Quiz oder Test ohne Fehler), Testlauf, Projekt geschafft, Level 3. **Meilensteine** (Zähler mit nächster Stufe): Abschnitte gelesen (10/25/50), Quizze bearbeitet (5/15/30), XP (250/500/1000). Die Auswahl ist bewusst klein; mehr bei Bedarf.
- **Nicht enthalten:** Tages-Serien (Streaks) und Zeitverläufe – dafür fehlt die Historie (`Fortschritt` speichert nur den letzten Stand), und der Wochen-/Tagesplan kommt mit B6.
- **Dashboard auf der Startseite unter den Themen** statt eigener Seite: weniger Navigation, Fortschritt ist sofort sichtbar. Das Frontend rechnet nichts, es zeigt nur an. Nach jeder Änderung des Fortschritts wird es neu geladen (gleicher Abfrage-Schlüssel wie der Fortschritt).
- **Trefferquote** = richtige Antworten / mögliche in den gespeicherten Bestwerten von Quizzen und Tests; ohne Ergebnis „noch kein Ergebnis“.
- **Folge der Berechnung aus dem Fortschritt:** Ändert sich später die Fragenzahl eines Quiz, ersetzt die neue Abgabe den Bestwert (B2); die XP können dadurch sinken. Für eine persönliche Lern-App akzeptabel und ehrlicher als veraltete Werte.

## 2026-11-03 – B6 Wochen- und Tagesplan

- **Blöcke fest im Code** (`backend/lernen/wochenplan.py`), gemäß `docs/LERNPLAN.md` („Tagesstruktur“): Montag bis Donnerstag Vormittag Theorie (ca. 3 Std.), Nachmittag Praxis und Quiz (ca. 2–3 Std.) sowie Englisch (30–45 Min.); Freitag Test, Wiederholung, Wochenauswertung und Englisch. **Keine festen Uhrzeiten**, da der Lernplan keine vorgibt. **Keine Themenzuordnung** je Block, da das Curriculum (C-Aufgaben) noch fehlt. Alternative: Blöcke in der Datenbank (ohne Eingabemöglichkeit nutzlos, mehr Aufwand).
- **Wochenauswertung aus `Fortschritt.erledigt_am`** (`auto_now`): Ein Eintrag zählt nur in der Woche seiner letzten Änderung, eine früher erledigte und später erneut bearbeitete Aufgabe wandert also in die neue Woche. Alternative: Verlaufstabelle mit jedem Ereignis (nicht im Backlog). Die Oberfläche zeigt dazu einen Hinweis.
- **Woche = Montag 0 Uhr bis Sonntag** in der Zeitzone Europe/Berlin, als halboffenes Intervall (Beginn eingeschlossen, nächster Montag ausgeschlossen). So gibt es keine Doppelzählung an der Wochengrenze.
- **Endpunkt `GET /api/wochenplan/?datum=JJJJ-MM-TT`** liefert die Woche, die das Datum enthält (ohne Angabe: heute). Erlaubt sind die Jahre 2000–2100, sonst `400` (Überlaufschutz bei Datumsrechnung).
- **Frontend:** eigene Seite `/plan`, die gewählte Woche steht in der URL (`?woche=`), damit Zurück-Taste und Neuladen funktionieren. Link „Plan“ in der Kopfzeile. Das Frontend zeigt nur an und rechnet nichts.
