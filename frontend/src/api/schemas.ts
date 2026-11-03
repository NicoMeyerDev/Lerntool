/**
 * zod-Schemas der API-Antworten. Sie prüfen zur Laufzeit, dass das Backend liefert,
 * was die Oberfläche erwartet, und erzeugen daraus die TypeScript-Typen.
 *
 * Feldnamen entsprechen dem Backend (backend/lernen/serializers.py).
 */
import { z } from 'zod'

/** Antwort von `POST /api/auth/login/`. */
export const tokenSchema = z.object({ token: z.string().min(1) })

/** Antwort ohne Inhalt (204). */
export const leerSchema = z.undefined()

/** Thema in der Übersicht. */
export const themaSchema = z.object({
  id: z.number(),
  titel: z.string(),
  slug: z.string(),
  beschreibung: z.string(),
  reihenfolge: z.number(),
})
export type Thema = z.infer<typeof themaSchema>
export const themenSchema = z.array(themaSchema)

/** Lektion in der Gliederung einer Phase. */
export const lektionKurzSchema = z.object({
  id: z.number(),
  titel: z.string(),
  slug: z.string(),
  zusammenfassung: z.string(),
  reihenfolge: z.number(),
})

/** Phase mit Lektionen und Projektaufgaben. */
export const phaseSchema = z.object({
  id: z.number(),
  titel: z.string(),
  slug: z.string(),
  beschreibung: z.string(),
  reihenfolge: z.number(),
  lektionen: z.array(lektionKurzSchema),
  projektaufgaben: z.array(
    z.object({ id: z.number(), titel: z.string(), reihenfolge: z.number() }),
  ),
})

/** Thema mit vollständiger Gliederung. */
export const themaDetailSchema = themaSchema.extend({ phasen: z.array(phaseSchema) })
export type ThemaDetail = z.infer<typeof themaDetailSchema>

/** Abschnitt einer Lektion mit Lerntext (Markdown). */
export const abschnittSchema = z.object({
  id: z.number(),
  titel: z.string(),
  inhalt: z.string(),
  reihenfolge: z.number(),
  quiz_id: z.number().nullable(),
})
export type Abschnitt = z.infer<typeof abschnittSchema>

/** Lektion mit Abschnitten und Quellen. */
export const lektionSchema = z.object({
  id: z.number(),
  phase: z.number(),
  titel: z.string(),
  slug: z.string(),
  zusammenfassung: z.string(),
  reihenfolge: z.number(),
  abschnitte: z.array(abschnittSchema),
  quellen: z.array(z.object({ titel: z.string(), url: z.string() })),
  test_id: z.number().nullable(),
})
export type Lektion = z.infer<typeof lektionSchema>

/** Quiz zum Beantworten (ohne Lösung). */
export const quizSchema = z.object({
  id: z.number(),
  abschnitt: z.number(),
  fragen: z.array(
    z.object({
      id: z.number(),
      text: z.string(),
      reihenfolge: z.number(),
      antworten: z.array(z.object({ id: z.number(), text: z.string(), reihenfolge: z.number() })),
    }),
  ),
})
export type Quiz = z.infer<typeof quizSchema>

/** Auswertung einer Quiz-Abgabe. */
export const quizErgebnisSchema = z.object({
  punkte: z.number(),
  max_punkte: z.number(),
  bestwert: z.number(),
  fragen: z.array(
    z.object({
      frage_id: z.number(),
      gewaehlte_antwort_id: z.number().nullable(),
      richtige_antwort_id: z.number().nullable(),
      ist_richtig: z.boolean(),
      erklaerung: z.string(),
    }),
  ),
})
export type QuizErgebnis = z.infer<typeof quizErgebnisSchema>

/** Ein Fortschritts-Eintrag des angemeldeten Nutzers. */
export const fortschrittSchema = z.object({
  id: z.number(),
  abschnitt: z.number().nullable(),
  quiz: z.number().nullable(),
  test: z.number().nullable(),
  projektaufgabe: z.number().nullable(),
  punkte: z.number().nullable(),
  max_punkte: z.number().nullable(),
  erledigt_am: z.string(),
})
export type Fortschritt = z.infer<typeof fortschrittSchema>
export const fortschrittListeSchema = z.array(fortschrittSchema)

/** Test zum Beantworten (ohne Lösung) mit Zeitlimit. */
export const testSchema = z.object({
  id: z.number(),
  lektion: z.number(),
  zeitlimit_minuten: z.number(),
  fragen: quizSchema.shape.fragen,
})
export type TestAufgabe = z.infer<typeof testSchema>

/** Antwort auf `POST /api/tests/<id>/start/`: Restzeit laut Server. */
export const testStartSchema = z.object({
  versuch_id: z.number(),
  gestartet_am: z.string(),
  endet_am: z.string(),
  sekunden_rest: z.number(),
})
export type TestStart = z.infer<typeof testStartSchema>

/** Projektaufgabe mit Checkliste und Stand des Nutzers. */
export const projektSchema = z.object({
  id: z.number(),
  phase: z.number(),
  titel: z.string(),
  beschreibung: z.string(),
  punkte: z.array(
    z.object({ id: z.number(), text: z.string(), reihenfolge: z.number(), erledigt: z.boolean() }),
  ),
  erledigt: z.number(),
  gesamt: z.number(),
  abgeschlossen: z.boolean(),
})
export type Projekt = z.infer<typeof projektSchema>

/** Dashboard: Statistiken, XP, Level, Abzeichen und Meilensteine (Berechnung im Backend). */
export const dashboardSchema = z.object({
  xp: z.number(),
  level: z.number(),
  xp_im_level: z.number(),
  xp_pro_level: z.number(),
  statistik: z.object({
    abschnitte_gelesen: z.number(),
    abschnitte_gesamt: z.number(),
    quizze_bearbeitet: z.number(),
    quizze_gesamt: z.number(),
    tests_bearbeitet: z.number(),
    tests_gesamt: z.number(),
    projekte_erledigt: z.number(),
    projekte_gesamt: z.number(),
    trefferquote_prozent: z.number().nullable(),
  }),
  themen: z.array(
    z.object({ slug: z.string(), titel: z.string(), erledigt: z.number(), gesamt: z.number() }),
  ),
  abzeichen: z.array(
    z.object({
      schluessel: z.string(),
      titel: z.string(),
      beschreibung: z.string(),
      erreicht: z.boolean(),
    }),
  ),
  meilensteine: z.array(
    z.object({
      schluessel: z.string(),
      titel: z.string(),
      aktuell: z.number(),
      ziel: z.number(),
      erreicht: z.boolean(),
    }),
  ),
})
export type Dashboard = z.infer<typeof dashboardSchema>

/** Wochen- und Tagesplan mit Wochenauswertung (Berechnung im Backend). */
export const wochenplanSchema = z.object({
  woche_start: z.string(),
  woche_ende: z.string(),
  vorherige_woche: z.string(),
  naechste_woche: z.string(),
  ist_aktuelle_woche: z.boolean(),
  tage: z.array(
    z.object({
      datum: z.string(),
      wochentag: z.string(),
      ist_heute: z.boolean(),
      bloecke: z.array(
        z.object({
          schluessel: z.string(),
          tageszeit: z.string(),
          titel: z.string(),
          beschreibung: z.string(),
          dauer: z.string(),
        }),
      ),
    }),
  ),
  auswertung: z.object({
    abschnitte_gelesen: z.number(),
    quizze_bearbeitet: z.number(),
    tests_bearbeitet: z.number(),
    projekte_erledigt: z.number(),
    trefferquote_prozent: z.number().nullable(),
  }),
})
export type Wochenplan = z.infer<typeof wochenplanSchema>
