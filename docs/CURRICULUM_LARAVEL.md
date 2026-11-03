# Curriculum Laravel (Gliederung)

Grundlage: [LERNPLAN.md](LERNPLAN.md), Themenblock 1. Diese Datei legt nur die **Gliederung** fest (Phasen, Themenfelder, Abschnitte, Projekte). Die ausgearbeiteten Lektionen kommen in C2 (Phase 1) und C3 (Phase 2); Phasen 3 bis 6 stehen später im Backlog.

## Regeln dieser Gliederung

- **Aufbau wie im Datenmodell:** Phase → Themenfeld (= Lektion, mit **Test** nach dem Themenfeld, max. 30 Min.) → Abschnitt (mit **Quiz** nach jedem Abschnitt) → **Projekt** am Ende der Phase.
- **Kein Vorwissen** in PHP und Laravel vorausgesetzt. Python-Vergleiche nur als Eselsbrücke.
- **Frontend ausgeklammert.** Laravel wird als reines Backend mit JSON-Antworten gelernt. Blade, Vite, Livewire und Inertia kommen nicht vor.
- **Eine Version:** Laravel 13 mit PHP 8.3 oder neuer (siehe „Versionen“). Vor jeder Ausarbeitung wird die Version in der Doku erneut geprüft.
- **Zeitangaben sind Richtwerte** für die Planung (eigene Schätzung, kein Fakt aus einer Quelle). Gesamt ca. 20 Wochen bei 5 Lerntagen pro Woche.

## Versionen (Stand 2026-11-03, geprüft)

| Was | Stand | Quelle |
| --- | --- | --- |
| Laravel 13 | Release 17. März 2026, benötigt mindestens PHP 8.3, unterstützt PHP 8.3 bis 8.5; Bugfixes bis Q3 2027, Sicherheitsfixes bis 17. März 2028 | [Laravel 13.x Release Notes](https://laravel.com/docs/13.x/releases) |
| Laravel 12 | Bugfixes liefen bis 13. August 2026, Sicherheitsfixes noch bis 24. Februar 2027 – deshalb nicht mehr für Neues wählen | [Laravel 13.x Release Notes](https://laravel.com/docs/13.x/releases) |
| PHP | 8.3: aktiver Support bis 31.12.2025, Sicherheitsfixes bis 31.12.2027. 8.4: aktiv bis 31.12.2026, Sicherheitsfixes bis 31.12.2028. 8.5 (Release 20.11.2025): aktiv bis 31.12.2027, Sicherheitsfixes bis 31.12.2029. 8.2 endet am 31.12.2026 | [PHP: Supported Versions](https://www.php.net/supported-versions.php) |

**Entscheidung für die Lektionen:** Laravel 13 mit **PHP 8.5**. Grund: von Laravel 13 unterstützt und bis 31.12.2027 aktiv gepflegt; PHP 8.4 verlöre den aktiven Support schon am 31.12.2026, mitten im Lernzeitraum. Die Lektionen vermeiden Besonderheiten einer einzelnen Version, sodass auch PHP 8.4 funktioniert (die Installationsbefehle auf [laravel.com/docs/13.x/installation](https://laravel.com/docs/13.x/installation) installieren PHP 8.4). Begründung steht in `docs/ENTSCHEIDUNGEN.md`.

## Gesamtüberblick

| Phase | Titel | Richtwert | Projekt |
| --- | --- | --- | --- |
| 1 | PHP-Basics | 3 Wochen | Trainingslog auf der Kommandozeile |
| 2 | Laravel-Kern | 5 Wochen | Trainingstagebuch (JSON-Backend mit Tests) |
| 3 | API und Authentifizierung | 4 Wochen | **Garmin-Auswertung, Teil 1:** Login, TCX-Import |
| 4 | Docker | 2 Wochen | **Garmin-Auswertung, Teil 2:** in Containern |
| 5 | Kubernetes (Grundlagen) | 2 Wochen | Manifeste für die Garmin-Auswertung |
| 6 | AWS und Cloudflare (Konzepte) | 2 Wochen | Architekturskizze für den Betrieb |
| Abschluss | Garmin-Auswertung fertigstellen (beim Import zweite Projektaufgabe von Phase 6, siehe „Hinweise zum Import“) | 2 Wochen | Kennzahlen und Auswertung |

---

## Phase 1: PHP-Basics

Quelle für die ganze Phase: [PHP-Handbuch](https://www.php.net/manual/en/) (php.net). Pro Themenfeld ein Test, pro Abschnitt ein Quiz.

### 1.1 Erste Schritte, Variablen und Typen
1. PHP-Skript ausführen, `echo`, Kommentare ([Basic syntax](https://www.php.net/manual/en/language.basic-syntax.php))
2. Variablen und Konstanten ([Variables](https://www.php.net/manual/en/language.variables.php))
3. Die Grundtypen: `int`, `float`, `string`, `bool`, `null` ([Types](https://www.php.net/manual/en/language.types.php))
4. Strings: Anführungszeichen, Verbinden, Einfügen von Variablen ([Strings](https://www.php.net/manual/en/language.types.string.php))
5. Typumwandlung und Vergleichen: `==` gegen `===` ([Type juggling](https://www.php.net/manual/en/language.types.type-juggling.php), [Comparison operators](https://www.php.net/manual/en/language.operators.comparison.php))

### 1.2 Operatoren und Kontrollstrukturen
1. Rechen-, Vergleichs- und logische Operatoren ([Operators](https://www.php.net/manual/en/language.operators.php))
2. Verzweigen: `if`, `else`, `match` ([Control structures](https://www.php.net/manual/en/language.control-structures.php))
3. Schleifen: `for`, `while`, `foreach` ([Control structures](https://www.php.net/manual/en/language.control-structures.php))
4. `break` und `continue`; Zusammenspiel von Schleife und Bedingung

### 1.3 Funktionen
1. Funktion definieren und aufrufen, Rückgabewert ([Functions](https://www.php.net/manual/en/language.functions.php))
2. Typdeklarationen für Parameter und Rückgabe, `declare(strict_types=1)` ([Type declarations](https://www.php.net/manual/en/language.types.declarations.php))
3. Standardwerte und benannte Argumente ([Function arguments](https://www.php.net/manual/en/functions.arguments.php))
4. Gültigkeitsbereich von Variablen ([Variable scope](https://www.php.net/manual/en/language.variables.scope.php))
5. Anonyme Funktionen und Pfeilfunktionen ([Anonymous functions](https://www.php.net/manual/en/functions.anonymous.php), [Arrow functions](https://www.php.net/manual/en/functions.arrow.php))

### 1.4 Arrays
1. Indizierte und assoziative Arrays anlegen und lesen ([Arrays](https://www.php.net/manual/en/language.types.array.php))
2. Ändern, Hinzufügen, Entfernen; Existenz prüfen
3. Über Arrays laufen mit `foreach`
4. Nützliche Funktionen: `count`, `in_array`, `array_map`, `array_filter`, `sort` ([Array functions](https://www.php.net/manual/en/ref.array.php))
5. Verschachtelte Arrays (Liste von Datensätzen)

### 1.5 Klassen und Objekte
1. Klasse, Objekt, Eigenschaften und Methoden ([Classes and objects](https://www.php.net/manual/en/language.oop5.php))
2. Konstruktor und Sichtbarkeit (`public`, `protected`, `private`)
3. Statische Mitglieder und Klassenkonstanten
4. Vererbung ([Inheritance](https://www.php.net/manual/en/language.oop5.inheritance.php))
5. Interfaces ([Object interfaces](https://www.php.net/manual/en/language.oop5.interfaces.php))
6. Enums als feste Auswahlwerte ([Enumerations](https://www.php.net/manual/en/language.enumerations.php))

### 1.6 Namespaces und Composer
1. Namespaces und `use` ([Namespaces](https://www.php.net/manual/en/language.namespaces.php))
2. Composer: `composer.json`, `require`, `install`, `composer.lock` ([Composer: Basic usage](https://getcomposer.org/doc/01-basic-usage.md))
3. Autoloading nach PSR-4 ([Composer: Autoloading](https://getcomposer.org/doc/04-schema.md#autoload))

### 1.7 Fehlerbehandlung
1. Fehler und Exceptions unterscheiden ([Error handling](https://www.php.net/manual/en/language.error-handling.php), [Throwable errors](https://www.php.net/manual/en/language.error-handling.throwable.php))
2. `try`, `catch`, `finally` ([try...catch](https://www.php.net/manual/en/control-structures.try-catch.php))
3. Eigene Exception-Klassen
4. Fehler nicht verschlucken: melden und protokollieren (`error_log`)

**Projekt Phase 1 – Trainingslog auf der Kommandozeile:** Ein PHP-Skript liest eine fest eingebaute Liste von Läufen (Datum, Distanz in km, Dauer in Minuten) und gibt Summe, Durchschnittstempo und den längsten Lauf aus. Verlangt: Klassen mit Namespace, Composer-Autoload, Typdeklarationen, eine eigene Exception für ungültige Werte. Checkliste mit 6 bis 8 Punkten.

---

## Phase 2: Laravel-Kern

Quelle für die ganze Phase: [Laravel 13.x Dokumentation](https://laravel.com/docs/13.x). Vor der Ausarbeitung (C3) wird jede Seite erneut gegen die Version geprüft.

### 2.1 Projekt und Aufbau
1. Anwendung anlegen, lokale Entwicklung starten ([Installation](https://laravel.com/docs/13.x/installation))
2. Ordnerstruktur ([Directory structure](https://laravel.com/docs/13.x/structure))
3. Konfiguration und `.env`, keine Zugangsdaten im Code ([Configuration](https://laravel.com/docs/13.x/configuration))
4. Weg einer Anfrage durch die Anwendung ([Request lifecycle](https://laravel.com/docs/13.x/lifecycle))
5. `artisan`-Befehle ([Artisan console](https://laravel.com/docs/13.x/artisan))

### 2.2 Routing
1. Routen definieren, Parameter ([Routing](https://laravel.com/docs/13.x/routing))
2. Benannte Routen und Gruppen
3. Middleware im Überblick ([Middleware](https://laravel.com/docs/13.x/middleware))

### 2.3 Controller, Anfragen und Antworten
1. Controller und Ressourcen-Controller ([Controllers](https://laravel.com/docs/13.x/controllers))
2. Eingaben der Anfrage lesen ([HTTP requests](https://laravel.com/docs/13.x/requests))
3. Antworten: JSON, Statuscodes, Weiterleitungen ([HTTP responses](https://laravel.com/docs/13.x/responses))

### 2.4 Datenbank und Migrationen
1. Datenbank anbinden ([Database: Getting started](https://laravel.com/docs/13.x/database))
2. Migrationen schreiben und ausführen ([Migrations](https://laravel.com/docs/13.x/migrations))
3. Query Builder: lesen, einfügen, ändern, löschen ([Query builder](https://laravel.com/docs/13.x/queries))
4. Testdaten mit Seedern ([Seeding](https://laravel.com/docs/13.x/seeding))

### 2.5 Eloquent
1. Modelle und Tabellen ([Eloquent: Getting started](https://laravel.com/docs/13.x/eloquent))
2. Anlegen, lesen, ändern, löschen (CRUD)
3. Beziehungen: eins-zu-viele, viele-zu-viele ([Relationships](https://laravel.com/docs/13.x/eloquent-relationships))
4. Das N+1-Problem und Eager Loading
5. Factories für Testdaten ([Factories](https://laravel.com/docs/13.x/eloquent-factories))

### 2.6 Validierung
1. Eingaben prüfen ([Validation](https://laravel.com/docs/13.x/validation))
2. Form Requests
3. Eigene Fehlermeldungen; Massenzuweisung absichern (`$fillable`)

### 2.7 Tests
1. Warum Tests; Pest oder PHPUnit ([Testing: Getting started](https://laravel.com/docs/13.x/testing))
2. HTTP-Tests für Routen und JSON ([HTTP tests](https://laravel.com/docs/13.x/http-tests))
3. Datenbank in Tests zurücksetzen ([Database testing](https://laravel.com/docs/13.x/database-testing))

**Projekt Phase 2 – Trainingstagebuch:** JSON-Backend für Trainingseinheiten (anlegen, auflisten, ändern, löschen) mit Migration, Eloquent-Modell, Validierung und Feature-Tests. Kein Frontend, keine Anmeldung (kommt in Phase 3). Checkliste mit 8 bis 10 Punkten.

---

## Phase 3: API und Authentifizierung

Quelle: [Laravel 13.x Dokumentation](https://laravel.com/docs/13.x) und [PHP-Handbuch](https://www.php.net/manual/en/).

### 3.1 API sauber gestalten
1. REST-Grundregeln: Ressourcen, Methoden, Statuscodes
2. API-Ressourcen für einheitliche JSON-Antworten ([Eloquent: API resources](https://laravel.com/docs/13.x/eloquent-resources))
3. Seitenweise Ausgabe ([Pagination](https://laravel.com/docs/13.x/pagination))
4. Fehlerantworten und Ausnahmen ([Error handling](https://laravel.com/docs/13.x/errors))

### 3.2 Authentifizierung mit Sanctum
1. Grundbegriffe: Authentifizierung gegen Autorisierung ([Authentication](https://laravel.com/docs/13.x/authentication))
2. API-Tokens mit Sanctum; Tokens laufen standardmäßig nicht ab, der Ablauf ist einstellbar ([Sanctum](https://laravel.com/docs/13.x/sanctum))
3. Registrieren, anmelden, abmelden über die API
4. Passwörter sicher speichern ([Hashing](https://laravel.com/docs/13.x/hashing))

### 3.3 Autorisierung
1. Gates und Policies ([Authorization](https://laravel.com/docs/13.x/authorization))
2. Jeder sieht nur seine eigenen Daten

### 3.4 Schutz und Qualität
1. Begrenzung von Anfragen ([Rate limiting](https://laravel.com/docs/13.x/routing#rate-limiting))
2. Häufige Sicherheitsrisiken einer API (Bezug zum DevSecOps-Kurs; [OWASP API Security](https://api-security.owasp.org/))
3. API-Tests mit Anmeldung ([HTTP tests](https://laravel.com/docs/13.x/http-tests))

### 3.5 Dateien und Hintergrundarbeit
1. Dateien hochladen und speichern ([File storage](https://laravel.com/docs/13.x/filesystem))
2. XML mit PHP lesen ([SimpleXML](https://www.php.net/manual/en/book.simplexml.php))
3. Aufgaben in die Warteschlange legen ([Queues](https://laravel.com/docs/13.x/queues))

**Projekt Phase 3 – Garmin-Auswertung, Teil 1:** API mit Anmeldung (Sanctum), Upload einer TCX-Datei, Import der Aktivität (Zeit, Distanz, Herzfrequenz) in die Datenbank, jeder Nutzer sieht nur seine Aktivitäten, Tests. Das TCX-Format wird anhand des offiziellen Garmin-Schemas erklärt ([TrainingCenterDatabasev2.xsd](https://www8.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd)).

---

## Phase 4: Docker

Quelle: [Docker-Dokumentation](https://docs.docker.com/).

### 4.1 Container verstehen
1. Image, Container, Registry ([Docker overview](https://docs.docker.com/get-started/docker-overview/))
2. Wichtige Befehle: `run`, `ps`, `logs`, `exec`, `stop`

### 4.2 Eigene Images
1. Dockerfile schreiben ([Dockerfile reference](https://docs.docker.com/reference/dockerfile/))
2. Eine Laravel-Anwendung in einen Container packen
3. Schichten, Cache und `.dockerignore`

### 4.3 Mehrere Container mit Compose
1. `compose.yaml` für App und Datenbank ([Docker Compose](https://docs.docker.com/compose/))
2. Netzwerk zwischen Containern
3. Daten behalten mit Volumes ([Volumes](https://docs.docker.com/engine/storage/volumes/))

### 4.4 Konfiguration und Sicherheit
1. Umgebungsvariablen statt fest eingebauter Werte; Umgang mit Secrets
2. Gute Praxis: kleine Images, kein Root-Nutzer ([Build best practices](https://docs.docker.com/build/building/best-practices/))

**Projekt Phase 4 – Garmin-Auswertung, Teil 2:** App, Datenbank und Warteschlangen-Worker laufen per `docker compose up`. Zugangsdaten nur über Umgebungsvariablen, `.env` nicht im Image.

---

## Phase 5: Kubernetes (Grundlagen)

Quelle: [Kubernetes-Dokumentation](https://kubernetes.io/docs/home/). Schwerpunkt: Konzepte verstehen und Manifeste lesen und schreiben. Ein lokaler Cluster ist optional.

### 5.1 Konzepte
1. Wozu Kubernetes: Cluster, Node, Pod ([Kubernetes components](https://kubernetes.io/docs/concepts/overview/components/))
2. Objekte und YAML-Manifeste ([Objects in Kubernetes](https://kubernetes.io/docs/concepts/overview/working-with-objects/))

### 5.2 Anwendungen betreiben
1. Pods und Deployments ([Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/))
2. Services und Ingress; die Ingress-API ist eingefroren, die Doku empfiehlt stattdessen die Gateway API ([Service](https://kubernetes.io/docs/concepts/services-networking/service/), [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/), [Gateway API](https://gateway-api.sigs.k8s.io/))
3. ConfigMaps und Secrets ([ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/), [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/))
4. Daten dauerhaft speichern ([Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/))

### 5.3 Bedienen und Fehler suchen
1. `kubectl` ([kubectl Quick Reference](https://kubernetes.io/docs/reference/kubectl/quick-reference/))
2. Logs lesen, Pods untersuchen, typische Fehlerbilder

**Projekt Phase 5:** Manifeste (Deployment, Service, ConfigMap, Secret-Vorlage ohne echte Werte) für die Garmin-Auswertung schreiben und mit der Kubernetes-Doku Punkt für Punkt prüfen. Ausführen nur in einem lokalen Cluster.

---

## Phase 6: AWS und Cloudflare (Konzepte)

Quellen: [AWS-Dokumentation](https://docs.aws.amazon.com/) und [Cloudflare-Dokumentation](https://developers.cloudflare.com/). Nur Konzepte und Theorie. **Kein echtes Konto und keine kostenpflichtigen Ressourcen ohne vorherige Rücksprache** (Kosten, CLAUDE.md Abschnitt 7).

### 6.1 Cloud-Grundlagen
1. Regionen, Verfügbarkeitszonen, geteilte Verantwortung ([AWS Shared Responsibility Model](https://aws.amazon.com/compliance/shared-responsibility-model/))

### 6.2 AWS-Bausteine
1. Zugriffsrechte mit IAM ([IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html))
2. Rechnen und Container-Dienste im Überblick
3. Objektspeicher S3 und Datenbank RDS ([S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html), [RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Welcome.html))
4. Netzwerk: VPC, Subnetze, Sicherheitsgruppen ([VPC](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html))

### 6.3 Cloudflare
1. DNS und Proxy ([Cloudflare DNS](https://developers.cloudflare.com/dns/))
2. HTTPS/TLS und Zwischenspeicher (CDN) ([SSL/TLS](https://developers.cloudflare.com/ssl/), [Cache](https://developers.cloudflare.com/cache/))
3. Schutz: WAF und DDoS-Schutz im Überblick ([WAF](https://developers.cloudflare.com/waf/))

### 6.4 Betrieb
1. Kosten im Blick behalten, Budgets und Warnungen
2. Sicherheit: geringste Rechte, keine Schlüssel im Code

**Projekt Phase 6:** Eine Architekturskizze (Text und Diagramm) für den Betrieb der Garmin-Auswertung: Wo laufen App, Datenbank und Dateien, wer darf was, was kostet es ungefähr (Annahmen offen benennen). Keine Umsetzung in der Cloud.

---

## Abschlussprojekt: Garmin-Auswertung

Baut über die Phasen 3 und 4 auf (Teile 1 und 2) und wird in der Abschlusszeit fertiggestellt. Backend in Laravel, kein Frontend. Beim Import ist es die **zweite Projektaufgabe von Phase 6** (Reihenfolge nach dem Architektur-Projekt); Checkliste mit 8 bis 10 Punkten.

1. **Kennzahlen:** Gesamtdistanz, Dauer, Durchschnittstempo und -herzfrequenz je Aktivität und je Woche.
2. **Auswertung:** Vergleich von Wochen, beste Aktivität, einfache Trends als JSON-Endpunkte.
3. **Qualität:** Tests, Validierung fehlerhafter Dateien, nachvollziehbare Fehlermeldungen.
4. **Betrieb:** Start mit Docker Compose, Dokumentation in einer README.

## Hinweise zum Import in die App

- **Zuordnung zum Datenmodell:** Thema „PHP/Laravel“ → Phase (1 bis 6) → Lektion = Themenfeld (z. B. 1.1) → Abschnitt (z. B. 1.1.3). Quiz hängt am Abschnitt, Test am Themenfeld, Projektaufgabe an der Phase. Das Abschlussprojekt ist eine zweite Projektaufgabe von Phase 6, damit es bei sechs Phasen bleibt.
- **Quellen:** Jede Lektion bekommt beim Import mindestens eine Quelle (Pflicht laut CLAUDE.md Abschnitt 5). Wo ein Abschnitt hier keinen eigenen Link hat, gilt die Phasenquelle als Mindestangabe und wird in der Ausarbeitung durch die konkrete Seite ersetzt.
- **Schreibweise:** Titel und Kurznamen (Slugs) je Phase und Themenfeld werden bei der Ausarbeitung (C2, C3) einmal festgelegt und danach nicht mehr geändert.
- **Kleine Themenfelder:** Hat ein Themenfeld nur einen oder zwei Abschnitte (z. B. 6.1, 2.2, 5.1), kann der Test dort kurz ausfallen oder das Feld wird bei der Ausarbeitung mit einem Nachbarn zusammengelegt.

## Offene Punkte (für die Ausarbeitung zu prüfen)

- **TCX-Format:** Belegt ist nur die XSD-Schemadatei von Garmin (siehe Projekt Phase 3). Eine erklärende Garmin-Dokumentation dazu wurde nicht gefunden; Erklärtexte müssen sich auf das Schema stützen, Sekundärseiten reichen nicht als Quelle.
- **Fehlende Links auf Abschnittsebene:** Einige Abschnitte nennen nur die Quelle der Phase (z. B. 4.1.2 Docker-Befehle, 4.2.3 `.dockerignore`, 6.1 Regionen und Verfügbarkeitszonen, 6.4 Kosten und Sicherheit). Die genauen Seiten werden bei der Ausarbeitung ergänzt und vom `quellenpruefer` geprüft.
- **Seiten-Adressen der Laravel-Doku:** Die Links oben folgen dem Schema `laravel.com/docs/13.x/<seite>`. Der `quellenpruefer` prüft jede Adresse; ein Link, der nicht erreichbar ist, wird in der Ausarbeitung ersetzt.
- **Pest oder PHPUnit:** Welches Test-Werkzeug die Laravel-Doku für ein neues Projekt vorschlägt, wird in C3 anhand der Version 13 festgelegt und in `docs/ENTSCHEIDUNGEN.md` vermerkt.
- **Rate Limiting und Sanctum-Details:** Genaue Seiten und Namen in Version 13 vor der Ausarbeitung von Phase 3 erneut prüfen.
