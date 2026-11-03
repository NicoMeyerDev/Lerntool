# Lernplan (Grundlage für alle Lerninhalte)

## Ziel
Berufseinstieg als Backend-Entwickler mit PHP/Laravel in ca. 5 Monaten. Gesamtzeitraum der App: ca. 6 Monate. Der Lernende ist die einzige Zielperson.

## Ausgangsstand
- Python und Django: Weiterbildung abgeschlossen. DevSecOps-Kurs abgeschlossen.
- PHP und Laravel: Grundlagen nur oberflächlich, deshalb von Grund auf und ohne Vorwissen lehren (Python-Vergleich nur als Eselsbrücke).
- Englisch: Basisniveau, Schwerpunkt Hören, Lesen, Schreiben (kein Mikrofon).
- Russisch: zurückgestellt.

## Lernstil
- Kurze bildliche Erklärung in einfacher Sprache, danach Beispiele.
- Grundlagen verstehen und sicher anwenden.
- Kleine, konkrete Schritte statt langer Mehrphasen-Pläne.
- Nur wenige Kernpunkte pro Lektion, kein unnötiges Drumherum.

## Tagesstruktur
5 Tage pro Woche, Wochenende frei. Vormittag Theorie (ca. 3 Std.), Nachmittag Praxis und Quiz (ca. 2-3 Std.), täglich 30-45 Min. Englisch. Freitag: Test, Wiederholung, Wochenauswertung.

## Themenblock 1: PHP/Laravel (Priorität 1)
Phasen:
1. PHP-Basics (Variablen, Typen, Kontrollstrukturen, Funktionen, Arrays, Klassen, Namespaces, Composer, Fehlerbehandlung)
2. Laravel-Kern (Routing, Controller, Eloquent, Migrationen, Validierung, Tests)
3. API-first und Authentifizierung
4. Docker
5. Kubernetes (Grundlagen)
6. AWS und Cloudflare (Konzepte)

Frontend ist ausgeklammert. Abschlussprojekt: Auswertung eigener Garmin-Sportdaten (TCX-Import, Kennzahlen, Auswertung), Backend in Laravel.

## Themenblock 2: Englisch
Pfad: Alltag und Ausland, dann Fachenglisch IT, optional Sprachtest am Ende.

## Themenblock 3: Wiederholung Backend (Django)
Themen: Internet-Architektur und HTTP, Python-Grundlagen, Django (Struktur, Routing, Templates, ORM), Datenbanken (Relationen, Admin, Queries, Aggregationen), Django REST Framework (Serializer, Pagination, Filter, Tests), Authentifizierung und Rechte, erweiterte Konzepte (Caching mit Redis, Task-Queues, Postgres, Dateimanagement), DevOps (Git, CI/CD, Cloud-Hosting), Monitoring (Fehlerüberwachung, Systemüberwachung), SQL und Optimierung.
Priorität: Auth, Datenbanken, API, Testing, CI/CD, Monitoring.

## Themenblock 4: Wiederholung DevSecOps
Themen: IT-Sicherheit und Recht (Schutzziele, Phasen von Angriffen, KRITIS, Ethical Hacking, OWASP), Python für Automation, Netzwerke und Protokolle, Linux (Konsole, SSH, Fail2ban), Web-Schwachstellen (XSS, Injection), Cloud (Container, Orchestrierung, Skalierung, WAF), DevSecOps (Security-by-Design, CI/CD, SAST/DAST, Observability), Datenschutz und Medienrecht, Passwort-Sicherheit.
Praktische Labs (Kali, Metasploitable, Juice Shop) nur als Theorie und Quiz abbilden.

## Themenblock 5: AI Engineering
Einstieg erst nach dem Start von PHP/Laravel und Englisch (Priorität nach Block 1 und 2).
Themen:
1. Grundlagen von Sprachmodellen (Tokens, Kontextfenster, Temperatur, Grenzen, typische Fehler wie erfundene Antworten)
2. Prompting (klare Anweisungen, Beispiele, Rollen, strukturierte Ausgabe)
3. Modelle über eine API ansprechen (Anfragen, Antworten, Fehlerbehandlung, Kosten und Limits)
4. Strukturierte Ausgaben und Tool-Nutzung (Function Calling)
5. Wissen anbinden (Embeddings, Vektorsuche, RAG)
6. Agenten (Aufbau, Schleifen, Grenzen, Kontrolle durch Regeln und Prüf-Agenten)
7. Qualität und Sicherheit (Bewertung von Ausgaben, Tests für KI-Funktionen, Prompt-Injection, Datenschutz)
8. KI-Funktionen in eine Anwendung einbauen (Backend-Anbindung, Kostenkontrolle, Zwischenspeicher)

Praxisprojekt: Die KI-Auswertung der Lern-App selbst (Schwächenanalyse, adaptive Aufgaben) als echtes Anwendungsbeispiel.
Quellen: offizielle Dokumentation der Modellanbieter (z. B. Anthropic) und anerkannte Fachquellen. Das Feld verändert sich schnell, deshalb prüft der Quellenprüfer bei jeder Aussage, ob sie noch zur aktuellen Version passt.

## Konzept-Vergleiche
Auth, Datenbanken, API, Testing, Docker und CI/CD als gemeinsame Lektionen mit zwei Umsetzungen: Django und Laravel.

## Regeln für Inhalte
Siehe CLAUDE.md, Abschnitt 5 (Quellen, Stil, Ablauf mit Quiz, Test, Projekt).
