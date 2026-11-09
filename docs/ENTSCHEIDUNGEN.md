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
- **API-Adresse über `VITE_API_URL`, lokal leer mit Vite-Proxy `/api` → `http://localhost:8000`** – lokal keine CORS-Einstellungen nötig (für das Deployment abgelöst durch den Eintrag vom 2026-11-05, Render-Deployment).
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

## 2026-11-03 – C1 Curriculum Laravel (Gliederung)

- **Laravel 13 statt 12.** Laravel 13 erschien am 17.03.2026 und benötigt PHP 8.3 oder neuer. Laravel 12 bekommt nur noch Sicherheitsfixes (bis 24.02.2027). Wer jetzt neu lernt, soll die aktuelle Version lernen. Quelle: laravel.com/docs/13.x/releases. Alternative: Laravel 12 (läuft früher aus, kein Vorteil).
- **PHP 8.5 als Lernversion statt 8.4.** PHP 8.4 verliert den aktiven Support am 31.12.2026, mitten im Lernzeitraum; 8.5 ist aktiv bis 31.12.2027. Die Lektionen vermeiden versionsspezifische Besonderheiten, sodass auch 8.4 funktioniert (der Laravel-Installationsbefehl installiert 8.4). Quelle: php.net/supported-versions.php. Alternative: 8.4 (kürzerer Support).
- **Abschlussprojekt Garmin-Auswertung als zweite Projektaufgabe von Phase 6.** Projektaufgaben sind im Datenmodell an eine Phase gebunden, und es soll bei 6 Phasen bleiben. Beim Import wird es daher als zweites Projekt der Phase 6 geführt. Alternative: eine siebte Phase „Abschluss“ (weicht von der Vorgabe mit 6 Phasen ab).
- **Teile 1 und 2 der Garmin-Auswertung** sind Projekte der Phasen 3 und 4.
- **Zeitrichtwerte (20 Wochen) sind eine eigene Schätzung**, nicht aus einer Quelle belegt.
- **TCX ist nur über die Garmin-XSD belegt** (www8.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd). Eine erklärende Garmin-Dokumentation wurde nicht gefunden; Aussagen zum Format stützen sich deshalb nur auf das Schema.

## 2026-11-03 – C2 Phase 1 PHP-Basics (Inhalte und Import)

- **Inhalte liegen als YAML-Dateien** in `backend/inhalte/<thema>/<NN>-<phase>/<NN>-<lektion>.yaml`, dazu `thema.yaml` und `phase.yaml` (mit Projekt und Checkliste). Die Nummer im Namen legt die Reihenfolge fest, der Rest ist der Kurzname. Grund: Markdown-Langtexte sind in YAML-Blockscalars gut lesbar und prüfbar. Alternativen: JSON (Zeilenumbrüche mühsam zu escapen), reine Markdown-Dateien (eigener Parser nötig), Python-Dicts (Inhalt als Code).
- **Neue Abhängigkeit PyYAML 6.0.3** (ausschließlich `safe_load`) und `types-PyYAML` für mypy.
- **Befehl `python manage.py import_inhalte [Ordner]`**, Logik in `lernen/inhalte_import.py`. Zuerst wird alles geprüft: Quelle mit http(s)-Link je Lektion, je Frage genau eine richtige Antwort, Test höchstens 30 Minuten, ein Quiz je Abschnitt, ein Test je Lektion, keine doppelten Nummern oder Kurznamen. Danach wird in einer Transaktion gespeichert. Der Import ist wiederholbar und löscht nie (bei fehlenden Lektionen, Abschnitten oder Checkpunkten gibt es nur eine Warnung). Quellen, Fragen und Antworten werden ersetzt, weil daran kein Fortschritt hängt (er hängt an Abschnitt, Quiz, Test und Projekt). Beim Umsortieren werden Positionen vorübergehend verschoben, damit die Eindeutigkeits-Regeln nicht kollidieren.
- **Bekannte Einschränkung:** Abschnitte, Projekte und Checklistenpunkte werden über ihre Position erkannt. Neue also nur hinten anhängen, sonst zeigt vorhandener Fortschritt auf anderen Inhalt. Ein Import während eines laufenden Tests oder Quiz im Browser kann dessen Abgabe ablehnen, weil sich die Frage-IDs ändern.
- **`weitere_projekte` in `phase.yaml`** ist für das Abschlussprojekt (Phase 6) vorbereitet, laut `docs/CURRICULUM_LARAVEL.md`.
- **Keine Tabellen in Lerntexten**, weil die Markdown-Darstellung im Frontend keine Tabellen kann (kein `remark-gfm`). Alternative: `remark-gfm` als neue Abhängigkeit.
- **Umfang Phase 1:** 7 Themenfelder, 32 Abschnitte mit je 3 Quizfragen, 7 Tests mit je 8 Fragen (Zeitlimit 20–25 Minuten), Projekt „Trainingslog“ mit 8 Checklistenpunkten.
- **Ergebnis der Quellenprüfung:** Klassen werden nie auf den globalen Namespace zurückgeführt, nur Funktionen und Konstanten (php.net, language.namespaces.fallback.php). Der Text wurde korrigiert.

## 2026-11-04 – C3 Phase 2 Laravel-Kern (Inhalte)

- **Lektionen lehren das Attribut `#[Fillable([...])]`**, weil die Laravel-13.x-Dokumentation nur dieses zeigt. Die ältere `$fillable`-Property wird nur als Hinweis erwähnt. Alternative: `$fillable` als Hauptweg (in der aktuellen Doku nicht mehr gezeigt).
- **Felder des Beispielprojekts „Trainingstagebuch“:** `datum`, `sportart`, `distanz_km`, `dauer_min`. Die Validierung nutzt die Obergrenzen `max:9999.99` und `max:1440`, passend zur Migration (Spaltengrößen). Grund: Eingaben, die die Datenbank nicht speichern kann, sollen schon bei der Validierung abgelehnt werden.
- **`response()->noContent()` ist nur in der API-Referenz belegt**, nicht im Handbuch. Deshalb steht zusätzlich api.laravel.com als Quelle in der Lektion.
- **Umfang Phase 2:** 7 Lektionen, Projekt „Trainingstagebuch“. Freigaben: `reviewer` FREIGABE, `quellenpruefer` FREIGABE.

## 2026-11-04 – C4 Englisch, Gliederung

- **Start bei Niveau A2 (aktualisiert am 2026-11-04).** Zuerst war A1 angenommen, weil „Einstieg ab SAP 2122“ unklar war. Der Lernende hat klargestellt: Gemeint ist sein heutiges Englisch, A2 (Selbsteinschätzung). Deshalb beginnt die Gliederung bei 1.3; 1.1 und 1.2 (A1) bleiben als optionale Wiederholung. Phase 1 schrumpft auf 6 Wochen (eigene Schätzung). Alternative: Einstufungstest vor dem Start (nicht im Backlog, daher nicht gebaut).
- **Drei Phasen:** Alltag und Ausland (A2, optional A1-Wiederholung), Fachenglisch IT (A2–B1), Sprachtest (optional). Entspricht dem Lernplan. B1 ist ein Wunschziel für den IT-Bereich, Zeitangaben sind eigene Schätzungen und stammen aus keiner Quelle.
- **Projekt Phase 2 knüpft an das Laravel-Projekt „Trainingstagebuch“ an**, damit Fachenglisch an echtem Material geübt wird (englische README, Pull-Request-Text). Alternative: eigenes, unabhängiges Beispiel.
- **Niveau-Zuordnung der Themenfelder ist eine eigene didaktische Einordnung**, keine offizielle Einstufung; sie wird bei der Ausarbeitung gegen die konkrete LearnEnglish-Seite geprüft.
- **Freigaben:** `quellenpruefer` NACHBESSERN (kleine Punkte, eingearbeitet), `reviewer` FREIGABE.

## 2026-11-04 – E1 AI Engineering

- **Quelle sind die Claude Docs unter platform.claude.com/docs/en** (Stand geprüft am 2026-11-04). Die alte Adresse docs.claude.com leitet dorthin um. Alternative: Quellen anderer Anbieter oder Blogs (laut Projektregeln nicht zulässig).
- **Keine Modellnamen, Preise und Limit-Zahlen in den Lektionen**, weil sie schnell veralten. Die Lektionen verweisen stattdessen auf die passenden Doku-Seiten. Alternative: konkrete Werte nennen (wären nach kurzer Zeit falsch und müssten ständig nachgepflegt werden).
- **Projekt Phase 1 ist ohne echten API-Aufruf lösbar**, weil Aufrufe Kosten und einen API-Schlüssel brauchen (siehe `docs/OFFEN.md`). Alternative: Projekt mit echten Aufrufen (erst nach Entscheidung des Lernenden zu Kosten und Schlüssel).
- **Phasen 2 bis 6 sind nur grob gegliedert**, die Ausarbeitung folgt in späteren Aufgaben. Grund: Die Doku ändert sich schnell, Details sollen erst kurz vor dem Lernen geprüft werden. Alternative: alle Phasen sofort ausarbeiten (höheres Risiko veralteter Inhalte).
- **`thema.yaml` hat `reihenfolge: 3`** (PHP/Laravel 1, Englisch 2 reserviert). Alternative: 2 vergeben und Englisch später verschieben (würde die Reihenfolge nachträglich ändern).
- **Freigaben:** `quellenpruefer` FREIGABE, `reviewer` FREIGABE.

## 2026-11-04 – Antworten des Lernenden zu C4/E1

- **Audio für Hörübungen (C4):** Eigene, gut verständliche Aufnahmen sind erlaubt. Ob echte Aufnahme oder Sprachausgabe, wird erst bei der Ausarbeitung der Hörlektionen entschieden, ohne Kosten und mit sauberer Lizenz. Grund: Fremde Audios dürfen nicht kopiert werden, Kosten sollen vermieden werden. Alternativen: Hörtexte nur verlinken (z. B. British Council LearnEnglish), Sprachausgabe im Browser, kostenpflichtige Sprachdienste (nicht gewollt).
- **API-Schlüssel (E1):** Der Lernende legt vorerst keinen API-Schlüssel an. Phase 1 kommt ohne Aufruf aus; Phasen mit echten Aufrufen sind bis zu einer neuen Entscheidung zurückgestellt. Grund: Kosten und Sicherheit des Schlüssels. Alternative: Schlüssel mit niedrigem Ausgabenlimit anlegen (aktuell nicht gewünscht).

## 2026-11-04 – C5 Englisch Phase 1

- **Entscheidung:** Phase 1 „Alltag und Ausland“ ab 1.3 (A2) ist in `backend/inhalte/englisch/` ausgearbeitet: 3 Lektionen mit Tests und das Projekt „Reiseplan“. Es gilt nur, was eine geprüfte Quelle (fast ausschließlich British Council LearnEnglish) hergibt; alles andere bleibt offen (siehe `OFFEN.md`, Abschnitt „Englisch (C5): Lücken in Phase 1“, und Backlog C6).
- **Grund:** CLAUDE.md Abschnitt 5: nichts erfinden, nur belegbare Aussagen. Lieber eine Lücke als ein unbelegter Inhalt.
- **Alternativen:** Lücken aus eigenem Wissen füllen (verworfen, kein Beleg); die ganze Aufgabe zurückstellen (verworfen, der belegte Teil ist sofort nutzbar).

Abweichungen von `docs/CURRICULUM_ENGLISCH.md`:

- **(a) 1.3.5 Hören ausgelassen.** Die Audio-Umsetzung steht aus (Backlog „Audio-Umsetzung“).
- **(b) 1.4.1 Reisen** (Bahn, Bus, Flug, Durchsagen) ausgelassen: keine belegte Quelle gefunden.
- **(c) 1.4.4 Restaurant und Arzt** ausgelassen: keine belegte Quelle.
- **(d) 1.5.5 Texte überfliegen** ausgelassen: keine belegte Quelle.
- **(e) 1.5.3 „Would you mind“ ausgelassen.** Die Gliederung erlaubt es nur bei Beleg; die LearnEnglish-Seite „Requests, offers and invitations“ nennt es nicht.
- **(f) 1.4.2 Wegbeschreibung** stützt sich auf ein LearnEnglish-Kids-PDF (British Council, Kinderniveau). Eine Erwachsenenseite wurde nicht gefunden.
- **(g) Zusätzlich aufgenommen, weil die Quelle es hergibt:** Abschnitt „Zwei Vergangenheiten zusammen“ (past continuous und past simple, A2-Seite) und „Ein Formular für die Unterkunft ausfüllen“ (A2-Aufgabe „An accommodation form“; in der Gliederung eigentlich 1.1.3, A1).
- **(h) Wortschatz** kommt nur als Teil der Lektionen vor, es gibt keinen eigenen Wortschatzabschnitt.
- **(i) „Persönliche E-Mails beginnen“** stützt sich auf eine B1-Seite; im Text als unsicher gekennzeichnet.
- **(j) Quellenlage:** Die Quelle ist fast nur British Council LearnEnglish. Für die Rechtschreibung der -ing-Form gibt es keine zweite unabhängige Quelle; sie ist als eigene Erklärung gekennzeichnet.
- **(k) Lektionsnamen:** `01-gerade-jetzt-und-vergangenes`, `02-unterwegs-im-ausland`, `03-schriftlicher-alltag`; `thema.yaml` hat `reihenfolge: 2`. Das Projekt „Reiseplan“ läuft in der App ohne Hörteil und mit 8 Punkten.

## 2026-11-04 – D1 Backend-Wiederholung, Teil 1

- **(a) Aufteilung:** D1 wird in mehrere kleine Teile zerlegt, Reihenfolge nach der Priorität im Backlog. Teil 1: Themen 3 Django, 4 Datenbanken, 5 DRF mit Testing, 6 Auth. Teil 2: 8 DevOps/CI/CD, 9 Monitoring. Teil 3: 1 HTTP, 2 Python, 7 erweiterte Konzepte, 10 SQL. Alternative: alles in einem Schritt (zu groß für eine Prüfung und ein Review).
- **(b) Quelle:** Die versionierte Django-Doku unter `/en/5.2/`, weil das Projekt Django 5.2 nutzt und die Seite „stable“ inzwischen Django 6.1 zeigt. Die DRF-Doku ist unversioniert; Stand geprüft am 2026-11-04. Alternative: „stable“ verlinken (würde Funktionen beschreiben, die im Projekt nicht gelten).
- **(c) Struktur:** `thema.yaml` hat `reihenfolge: 4`. Die Phasen-Ordner tragen die Nummer des Themas aus dem Lernplan (03 bis 06). Lücken in der Nummerierung sind gewollt und vom Importer erlaubt. Alternative: fortlaufend 01 bis 04 nummerieren (Bezug zum Lernplan ginge verloren).
- **(d) Form:** Als Wiederholung formuliert, je Themenfeld ein bis drei Lektionen mit drei Abschnitten, je Phase ein kleines Projekt. Alternative: ausführliche Einführung (nicht nötig, Vorwissen ist laut Lernplan vorhanden).
- **(e) Umfang Thema 5:** „DRF“ umfasst Serializer, Views und Router, Pagination und Filter sowie Tests. Themen aus 7 (Caching, Task-Queues, Dateimanagement) kommen bewusst erst in Teil 3. Alternative: alles zu 7 jetzt mitnehmen (Teil 1 würde zu groß).
- **(f) Antwortreihenfolge:** Die richtige Antwort ist gleichmäßig auf die Positionen verteilt, weil die App die Antworten nicht mischt (siehe `OFFEN.md`). Alternative: immer an erster Stelle (würde erratbar).
- **Freigaben:** `quellenpruefer` und `reviewer` (Runde 2) stehen vor dem Merge noch aus.

## 2026-11-04 – D1 Backend-Wiederholung, Teil 2 (DevOps und Monitoring)

- **(a) Projekte auf Papier:** Die Projekte der Phasen 08 und 09 werden auf Papier bearbeitet. Es wird kein Konto, kein Server und keine kostenpflichtige Leistung eingerichtet (CLAUDE.md Abschnitt 7: Kosten und Sicherheit). Alternative: echtes Deployment bei Render (Kosten, Zugangsdaten).
- **(b) Nur erklärt, nicht eingerichtet:** Render, Sentry und Prometheus werden in den Lektionen erklärt, aber nicht eingerichtet. Alternative: Konten anlegen (siehe a).
- **(c) Eigene Regeln gekennzeichnet:** Regeln aus diesem Projekt (z. B. keine Secrets im Code, Zugangsdaten nur über Umgebungsvariablen) und eigene Ratschläge sind in den Lektionen als „Eigene Regel“ bzw. „Eigener Rat“ markiert und nicht als Aussage der Quelle dargestellt.
- **(d) Sentry SDK 3.0:** Die Lektion weist darauf hin, dass sich Einrichtung und Optionen mit SDK 3.0 ändern können; maßgeblich ist die aktuelle Sentry-Doku. Alternative: nur die ältere Variante zeigen (würde veralten).
- **Freigaben:** `quellenpruefer`: FREIGABE (alle Quellen erreichbar). `reviewer`: FREIGABE nach 2 Runden.

## 2026-11-05 – Render-Deployment vorbereitet

- **Frontend und Backend als getrennte Render-Dienste** (statische Seite + Web-Service), Verbindung per CORS (`django-cors-headers`) und `VITE_API_URL`. Grund: Architektur aus CLAUDE.md bleibt strikt getrennt. Alternative: Rewrite `/api/*` auf das Backend (braucht die Backend-Adresse schon in `render.yaml`) oder Frontend über Django ausliefern.
- **Migration, Inhalts-Import und Nutzeranlage im `startCommand`** statt `preDeployCommand`. Grund: Die Render-Doku nennt für den kostenlosen Tarif keine Zusage für Pre-Deploy-Befehle und keinen Shell-Zugang. Alle drei Befehle sind wiederholbar. Alternative: `preDeployCommand` (bezahlter Tarif).
- **Befehl `anlegen_nutzer`** legt den einzigen Nutzer aus `LERNTOOL_BENUTZER`/`LERNTOOL_PASSWORT` an, nur wenn noch keiner existiert. Grund: ohne Shell kein `createsuperuser`. Alternative: `createsuperuser --noinput` (schlägt beim zweiten Start fehl).
- **HTTPS-Absicherung nur mit `DJANGO_HTTPS_ERZWINGEN=True`**, nicht an `DEBUG` gekoppelt. Grund: Tests und CI laufen ohne HTTPS. Der Health-Check ist von der Umleitung ausgenommen. HSTS nur 1 Stunde, ohne Subdomains/Preload, weil `onrender.com` nicht dir gehört.
- **Kein `whitenoise`**, keine statischen Dateien aus Django: Die API liefert nur JSON.
- **Kostenlose Datenbank läuft nach 30 Tagen ab** (Render-Doku, Stand 2026-11-05). Entscheidung über einen bezahlten Tarif liegt beim Nutzer, siehe `docs/OFFEN.md`.

## 2026-11-05 – D1 Backend-Wiederholung, Teil 3 (HTTP, Python, erweiterte Konzepte, SQL)

- **(a) Versionen der Quellen:** Python-Quellen sind auf Version 3.13 festgelegt (`/3.13/`), Django auf 5.2. Grund: `/3/` zeigt auf 3.14, und dort ist `except` ohne Klammern erlaubt (PEP 758); das hätte eine Quizfrage mehrdeutig gemacht. Alternative: `/3/` ohne Version.
- **(b) Nur Theorie und Papier:** Redis, Celery und PostgreSQL werden nur erklärt und im Projekt auf Papier bearbeitet. Es wird kein Dienst eingerichtet, es entstehen keine Kosten. Alternative: Dienste lokal oder gehostet einrichten (Aufwand, Kosten).
- **(c) Celery unter Windows:** Laut Doku wird Celery unter Windows nicht offiziell unterstützt. Die Lektion enthält einen Hinweis; die Empfehlung WSL oder Docker ist eine eigene Empfehlung und als solche gekennzeichnet.

## 2026-11-05 – D2 DevSecOps-Wiederholung

- **(a) Labs nur Theorie:** Die praktischen Labs (Kali, Metasploitable, Juice Shop) werden nur als Theorie und Quiz behandelt, nichts wird eingerichtet oder angegriffen (CLAUDE.md Abschnitt 7: Sicherheit). Alternative: Labs lokal aufbauen (Aufwand, Risiko bei Fehlbedienung).
- **(b) Quellen:** BSI (Grundschutz und Veröffentlichungen), KRITISDachG, NIST SP 800-63B-4 (Passwörter) und OWASP Top 10 2025. Nur offizielle Quellen, keine Foren oder Blogs.
- **(c) Keine Rechtsberatung:** Die Lektionen zu Datenschutz und Recht erklären nur Grundlagen und sind keine Rechtsberatung. Alternative: Rechtsthemen weglassen (wäre für den Kurs zu lückenhaft).
- **Freigaben:** `quellenpruefer`: Nachbesserungen in Runde 1, KRITIS-Quelle korrigiert. `reviewer`: FREIGABE in Runde 2 (nur Nachprüfung).

## 2026-11-05 – Quizqualität (Antwortlänge und Position)

- **Falschantworten als plausible Verwechslungen, richtige Antwort zyklisch auf Position 1/2/3** – verhindert, dass die Länge oder Position die Lösung verrät. Alternative: Mischen im Frontend (bleibt als Idee im Backlog).
- **Ausnahmen:** Bei Codeantworten und Fachdefinitionen bleibt die richtige Antwort teils die längste. Bei Grammatikfragen sind falsche Antworten bewusst Fehlerformen.
- **Umfang:** Nur Antworttexte, keine Fakten geändert. `reviewer`: FREIGABE nach zwei Runden.

## 2026-11-05 – D3 Konzept-Vergleiche Django und Laravel

- **(a) Aufbau:** Neues Thema `django-laravel-vergleich` (Reihenfolge 6) mit einer Phase und sechs Vergleichs-Lektionen: Anmeldung und Passwörter, Datenbank und Migrationen, API, Tests, Docker, CI/CD. Jede Lektion zeigt dieselbe Aufgabe in Django und Laravel. Alternative: getrennte Lektionen je Framework (verdeckt die gemeinsame Idee).
- **(b) PHP-CI-Schritte (2026-11-05 belegt):** Die Schritte für PHP/Laravel in GitHub Actions stützen sich jetzt auf die `setup-php`-README, die Composer-Doku und die Laravel-Testing-Doku statt auf php.net. Grund: php.net beschreibt keine CI-Abläufe. Alternative: Abschnitt weglassen (Vergleich unvollständig).
- **(c) Nur Theorie:** Es wird nichts eingerichtet, keine Konten, keine Kosten.

## 2026-11-05 – Quizqualität D2/D3

- **Vorgehen:** Die Antwortzeilen wurden skriptgestützt ersetzt. Falsche Antworten sind typische Verwechslungen in ähnlicher Länge wie die richtige Antwort. Die richtige Antwort wird gleichmäßig auf Position 1, 2 und 3 gedreht (zyklisch). Alternative: nur im Frontend mischen (löst die Längenauffälligkeit nicht).
- **Grenze:** Bei Fachdefinitionen und Rechtstexten bleibt die richtige Antwort oft die längste, weil Genauigkeit Länge braucht. Das wurde nicht künstlich erzwungen, um keine Fakten zu verfälschen.
- **Freigabe:** `reviewer`: FREIGABE (nur Hinweise, behoben).

## 2026-11-09 – Einheitenlänge: 20 bis 30 Minuten statt kurzer Lektionen

- **Entscheidung:** Eine Einheit soll **mindestens 20 Minuten** (Wunsch des Lernenden), höchstens rund 30 Minuten beschäftigen (Lesen, Aufgaben, Quiz). **Einheit ist ein Abschnitt samt Quiz**, denn die App zeigt eine Lektion Abschnitt für Abschnitt. Eine Lektion hat meist 3 bis 4 Abschnitte und dauert entsprechend länger. Dafür bekommt jeder Abschnitt etwas mehr Erklärung, eine Merkhilfe oder typische Fehler, mindestens eine „Probier es selbst“-Aufgabe mit Kontrolle und zusätzliche Quizfragen.
- **Abweichung vom Lernplan:** Der Lernstil in `docs/LERNPLAN.md` nennt „kurze bildliche Erklärung“ und „nur wenige Kernpunkte pro Lektion“. Das bleibt der Stil jedes Abschnitts (einfache Sprache, Bilder, Beispiele). Neu ist die Dauer der Einheit. Auslöser: Der Nutzer fand die Einheiten beim Ausprobieren zu kurz (rund 3 bis 5 Minuten Text plus Quiz).
- **Umsetzung:** Die Aufgaben stehen als Markdown im Lektionstext (Überschrift „Probier es selbst“), das Frontend rendert Markdown schon. Kein neues Datenfeld, keine Änderung an Import oder Frontend. Alternative: eigenes Feld `aufgaben` im Schema (bessere Auswertung, aber Änderungen an Import, API und Frontend, nicht gefordert).
- **Kontrolle der Aufgaben:** Jede Aufgabe nennt die erwartete Ausgabe. Es gibt keine automatische Auswertung. Alternative: Aufgaben im Browser ausführen (Kosten und Sicherheit, nicht im Backlog).
- **Vorgehen:** Erst eine Musterlektion, dann Freigabe durch den Nutzer, dann Thema für Thema. Jede Lektion geht durch `quellenpruefer` und `reviewer`.

## 2026-11-09 – Qualifizierungsplan des künftigen Arbeitgebers als Orientierung

- **Entscheidung:** Der Plan des künftigen Arbeitgebers (Schwerpunkt PHP und Laravel) dient als Orientierung für die Reihenfolge und die Themen des Laravel-Curriculums. Er ersetzt `docs/LERNPLAN.md` nicht, sondern ergänzt ihn. Fehlende Themen stehen im Backlog unter F2.
- **Datenschutz:** Namen von Firma und Betreuern und andere persönliche Angaben aus dem Plan stehen nicht im Repository, nur die Themen. Grund: Das Repository liegt auf GitHub. Alternative: Plan im Wortlaut ablegen (unnötig, enthält Personendaten).
- **Reihenfolge (Vorschlag, noch nicht umgesetzt):** Laut Plan folgen auf Laravel-Grundlagen zuerst Datenbank, API, Auth, Queues, Tests und Performance. Docker, Kubernetes und AWS kommen im Plan nicht vor und rücken im Curriculum hinter diese Themen. Die Änderung wird mit F2 gemacht und dort begründet.
