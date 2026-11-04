# Curriculum AI Engineering (Gliederung)

Grundlage: [LERNPLAN.md](LERNPLAN.md), Themenblock 5. Diese Datei legt die **Gliederung** fest (Phasen, Themenfelder, Abschnitte, Projekte). **Phase 1 (Themen 1 bis 3) ist mit Aufgabe E1 ausgearbeitet** (`backend/inhalte/ai-engineering/01-grundlagen/`). Die Phasen 2 bis 6 sind nur grob gegliedert und werden später ausgearbeitet.

## Regeln dieser Gliederung

- **Aufbau wie im Datenmodell:** Phase → Themenfeld (= Lektion, mit **Test** nach dem Themenfeld, max. 30 Min.) → Abschnitt (mit **Quiz** nach jedem Abschnitt) → **Projekt** am Ende der Phase.
- **Einstieg erst nach dem Start von PHP/Laravel und Englisch** (Lernplan, Themenblock 5).
- **Das Feld ändert sich schnell.** Darum prüft der `quellenpruefer` bei jeder Aussage, ob sie zur aktuellen Doku passt. Modellnamen, Preise, Limits und Versionsnummern stehen in den Lektionen **nicht fest**, sondern verweisen auf die Doku-Seite. Stand der Doku für Phase 1: geprüft am 2026-11-04.
- **Kosten:** Echte API-Aufrufe brauchen einen API-Schlüssel und kosten Geld. Projekte sind deshalb so geschnitten, dass sie **ohne** echten Aufruf lösbar sind. Ein Live-Aufruf ist freiwillig (siehe `docs/OFFEN.md`).
- **Zeitangaben sind Richtwerte** (eigene Schätzung, kein Fakt aus einer Quelle).

## Quellen

| Zweck | Quelle |
| --- | --- |
| API, Modelle, Prompting, Limits, Preise | [Claude Docs](https://platform.claude.com/docs/en/home) (Anthropic) |
| Weitere Fachquellen (Phasen 2 bis 6) | Offizielle Dokumentation der Anbieter und anerkannte Fachquellen, vom `quellenpruefer` je Lektion bestätigt |

## Gesamtüberblick

| Phase | Titel | Themen im Lernplan | Richtwert | Projekt | Stand |
| --- | --- | --- | --- | --- | --- |
| 1 | Grundlagen, Prompting und API | 1 bis 3 | 3 Wochen | Prompt- und API-Werkstatt | **ausgearbeitet (E1)** |
| 2 | Strukturierte Ausgaben und Werkzeuge | 4 | 2 Wochen | offen | Gliederung |
| 3 | Wissen anbinden (Embeddings, RAG) | 5 | 3 Wochen | offen | Gliederung |
| 4 | Agenten | 6 | 3 Wochen | offen | Gliederung |
| 5 | Qualität und Sicherheit | 7 | 2 Wochen | offen | Gliederung |
| 6 | KI in eine Anwendung einbauen | 8 | 3 Wochen | **KI-Auswertung der Lern-App** | Gliederung |

---

## Phase 1: Grundlagen, Prompting und API (ausgearbeitet)

Quelle: [Claude Docs](https://platform.claude.com/docs/en/home).

### 1.1 Wie Sprachmodelle arbeiten
1. Was ist ein Sprachmodell? (Pretraining, Nachtraining) ([Glossary](https://platform.claude.com/docs/en/about-claude/glossary))
2. Tokens und Kontextfenster ([Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows))
3. Temperatur und Zufall ([Glossary](https://platform.claude.com/docs/en/about-claude/glossary))
4. Grenzen und Halluzinationen ([Reduce hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations))

### 1.2 Prompting
1. Klar und direkt formulieren ([Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices))
2. Beispiele geben (Few-Shot)
3. Struktur mit XML-Tags und Rolle
4. Ausgabeformat steuern und Prompts an Kriterien testen ([Prompt engineering overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview))

### 1.3 Modelle über die API ansprechen
1. Eine Anfrage aufbauen ([Messages API](https://platform.claude.com/docs/en/api/messages))
2. Die Antwort lesen
3. Fehler behandeln ([Errors](https://platform.claude.com/docs/en/api/errors))
4. Kosten, Limits und Schlüssel ([Rate limits](https://platform.claude.com/docs/en/api/rate-limits), [Pricing](https://platform.claude.com/docs/en/about-claude/pricing), [Authentication](https://platform.claude.com/docs/en/manage-claude/authentication))

**Projekt Phase 1 – Prompt- und API-Werkstatt:** Erfolgskriterien festlegen, zwei Prompts an fünf Testeingaben vergleichen, eine API-Anfrage aufbauen, Fehlerbehandlung und Kosten überschlagen, eine Antwort auf Erfundenes prüfen. 8 Checklistenpunkte. Ein echter Aufruf ist freiwillig.

---

## Phase 2: Strukturierte Ausgaben und Werkzeuge (Gliederung)

Themenfelder (grob, noch ohne Abschnitte): Antworten in festem JSON-Format; Schema und Prüfung; Werkzeuge definieren und aufrufen lassen (Function Calling); Fehlerfälle bei Werkzeugen. Quelle voraussichtlich die Claude Docs; genaue Seiten und Versionsstand vor der Ausarbeitung prüfen.

## Phase 3: Wissen anbinden (Gliederung)

Themenfelder (grob): Embeddings und Ähnlichkeit; Vektorsuche; Aufbau von RAG (Dokumente zerteilen, suchen, in den Prompt geben); Qualität von Treffern. Quellen vor der Ausarbeitung festlegen.

## Phase 4: Agenten (Gliederung)

Themenfelder (grob): Aufbau und Schleife eines Agenten; Werkzeuge und Grenzen; Kontrolle durch Regeln und Prüf-Agenten; Kosten und Abbruchbedingungen. Passt zum Agenten-Team dieses Projekts als Anschauungsbeispiel.

## Phase 5: Qualität und Sicherheit (Gliederung)

Themenfelder (grob): Ausgaben bewerten (Evals); Tests für KI-Funktionen; Prompt-Injection; Datenschutz und was an eine API geschickt wird. Quellen: Anbieter-Doku und anerkannte Fachquellen (z. B. OWASP), vom `quellenpruefer` zu bestätigen.

## Phase 6: KI in eine Anwendung einbauen (Gliederung)

Themenfelder (grob): Anbindung im Backend (Service, Konfiguration, Fehler); Kostenkontrolle; Zwischenspeicher (Caching); Einbindung in die Lern-App.

**Praxisprojekt:** Die KI-Auswertung der Lern-App selbst (Schwächenanalyse, adaptive Aufgaben) als echtes Anwendungsbeispiel. Es entspricht dem offenen Backlog-Punkt „KI-Analyse der Schwächen und adaptive Aufgaben“ und startet erst nach Freigabe.

---

## Hinweise zum Import in die App

- **Zuordnung zum Datenmodell:** Thema „AI Engineering“ → Phase (1 bis 6) → Lektion = Themenfeld (z. B. 1.1) → Abschnitt (z. B. 1.1.3). Quiz hängt am Abschnitt, Test am Themenfeld, Projektaufgabe an der Phase.
- **Dateien:** `backend/inhalte/ai-engineering/` (`thema.yaml`, Ordner je Phase, eine YAML-Datei je Lektion). Import mit `python manage.py import_inhalte`.
- **Quellen:** Jede Lektion hat mindestens eine Quelle mit Link (Pflicht laut CLAUDE.md Abschnitt 5).

## Offene Punkte

- **Echte API-Aufrufe und Kosten:** Wer den Schlüssel anlegt, welches Limit gilt und ob Live-Aufrufe in Projekten erwartet werden, ist offen (siehe `docs/OFFEN.md`).
- **Veraltung:** Modelle, Preise und Limits ändern sich. Vor jeder Ausarbeitung einer weiteren Phase werden die Doku-Seiten erneut geprüft.
- **Phasen 2 bis 6:** Abschnitte, Quellen und Projekte sind noch festzulegen.
