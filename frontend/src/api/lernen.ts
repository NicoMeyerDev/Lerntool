/**
 * React-Hooks für die Lern-API (TanStack Query). Reine Datenbeschaffung, keine
 * Geschäftslogik: Auswertung und Speichern übernimmt das Backend.
 */
import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseMutationResult,
  type UseQueryResult,
} from '@tanstack/react-query'

import { apiAnfrage } from './client'
import {
  dashboardSchema,
  fortschrittListeSchema,
  fortschrittSchema,
  lektionSchema,
  projektSchema,
  quizErgebnisSchema,
  quizSchema,
  testSchema,
  testStartSchema,
  themaDetailSchema,
  themenSchema,
  wochenplanSchema,
  type Dashboard,
  type Fortschritt,
  type Lektion,
  type Projekt,
  type Quiz,
  type QuizErgebnis,
  type TestAufgabe,
  type TestStart,
  type Thema,
  type ThemaDetail,
  type Wochenplan,
} from './schemas'

/** Abfrage-Schlüssel für den Fortschritt (wird nach Änderungen neu geladen). */
const FORTSCHRITT_SCHLUESSEL = ['fortschritt'] as const

/**
 * Lädt alle Themen.
 *
 * @returns Abfrage-Zustand mit der Themenliste.
 */
export function useThemen(): UseQueryResult<Thema[]> {
  return useQuery({
    queryKey: ['themen'],
    queryFn: () => apiAnfrage('/api/themen/', themenSchema),
  })
}

/**
 * Lädt ein Thema mit Gliederung.
 *
 * @param slug - Kurzname des Themas aus der URL.
 * @returns Abfrage-Zustand mit dem Thema.
 */
export function useThema(slug: string): UseQueryResult<ThemaDetail> {
  return useQuery({
    queryKey: ['thema', slug],
    queryFn: () => apiAnfrage(`/api/themen/${encodeURIComponent(slug)}/`, themaDetailSchema),
  })
}

/**
 * Lädt eine Lektion mit Abschnitten und Quellen.
 *
 * Bei einer ungültigen ID (keine positive ganze Zahl) wird nichts angefragt.
 *
 * @param id - ID der Lektion.
 * @returns Abfrage-Zustand mit der Lektion.
 */
export function useLektion(id: number): UseQueryResult<Lektion> {
  return useQuery({
    queryKey: ['lektion', id],
    queryFn: () => apiAnfrage(`/api/lektionen/${String(id)}/`, lektionSchema),
    enabled: Number.isInteger(id) && id >= 1,
  })
}

/**
 * Lädt ein Quiz (ohne Lösung).
 *
 * @param id - ID des Quiz.
 * @returns Abfrage-Zustand mit dem Quiz.
 */
export function useQuiz(id: number): UseQueryResult<Quiz> {
  return useQuery({
    queryKey: ['quiz', id],
    queryFn: () => apiAnfrage(`/api/quizze/${String(id)}/`, quizSchema),
  })
}

/**
 * Lädt den Fortschritt des angemeldeten Nutzers.
 *
 * @returns Abfrage-Zustand mit allen Fortschritts-Einträgen.
 */
export function useFortschritt(): UseQueryResult<Fortschritt[]> {
  return useQuery({
    queryKey: FORTSCHRITT_SCHLUESSEL,
    queryFn: () => apiAnfrage('/api/fortschritt/', fortschrittListeSchema),
  })
}

/** Eine gewählte Antwort für die Quiz-Abgabe. */
export interface Auswahl {
  frage: number
  antwort: number
}

/**
 * Gibt ein Quiz ab. Das Backend wertet aus und speichert den Bestwert.
 *
 * @param quizId - ID des Quiz.
 * @returns Mutation, die die Auswertung liefert.
 */
export function useQuizAbgabe(quizId: number): UseMutationResult<QuizErgebnis, Error, Auswahl[]> {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (antworten: Auswahl[]) =>
      apiAnfrage(`/api/quizze/${String(quizId)}/abgabe/`, quizErgebnisSchema, {
        method: 'POST',
        body: { antworten },
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: FORTSCHRITT_SCHLUESSEL }),
  })
}

/**
 * Markiert einen Abschnitt als gelesen.
 *
 * @returns Mutation, die die ID des Abschnitts erwartet.
 */
export function useAbschnittGelesen(): UseMutationResult<Fortschritt, Error, number> {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (abschnittId: number) =>
      apiAnfrage(`/api/abschnitte/${String(abschnittId)}/gelesen/`, fortschrittSchema, {
        method: 'POST',
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: FORTSCHRITT_SCHLUESSEL }),
  })
}

/**
 * Lädt einen Test (ohne Lösung) mit Zeitlimit.
 *
 * @param id - ID des Tests.
 * @returns Abfrage-Zustand mit dem Test.
 */
export function useTest(id: number): UseQueryResult<TestAufgabe> {
  return useQuery({
    queryKey: ['test', id],
    queryFn: () => apiAnfrage(`/api/tests/${String(id)}/`, testSchema),
    enabled: Number.isInteger(id) && id >= 1,
  })
}

/**
 * Startet einen Testversuch. Der Server startet die Uhr und liefert die Restzeit;
 * ein bereits laufender Versuch wird fortgesetzt.
 *
 * @param testId - ID des Tests.
 * @returns Mutation, die Start und Restzeit liefert.
 */
export function useTestStart(testId: number): UseMutationResult<TestStart, Error, void> {
  return useMutation({
    mutationFn: () =>
      apiAnfrage(`/api/tests/${String(testId)}/start/`, testStartSchema, { method: 'POST' }),
  })
}

/**
 * Gibt einen Test ab. Das Backend prüft das Zeitlimit, wertet aus und speichert den Bestwert.
 *
 * @param testId - ID des Tests.
 * @returns Mutation, die die Auswertung liefert.
 */
export function useTestAbgabe(testId: number): UseMutationResult<QuizErgebnis, Error, Auswahl[]> {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (antworten: Auswahl[]) =>
      apiAnfrage(`/api/tests/${String(testId)}/abgabe/`, quizErgebnisSchema, {
        method: 'POST',
        body: { antworten },
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: FORTSCHRITT_SCHLUESSEL }),
  })
}

/**
 * Lädt eine Projektaufgabe mit Checkliste und Stand.
 *
 * @param id - ID der Projektaufgabe.
 * @returns Abfrage-Zustand mit der Projektaufgabe.
 */
export function useProjekt(id: number): UseQueryResult<Projekt> {
  return useQuery({
    queryKey: ['projekt', id],
    queryFn: () => apiAnfrage(`/api/projekte/${String(id)}/`, projektSchema),
    enabled: Number.isInteger(id) && id >= 1,
  })
}

/** Eingabe für {@link useProjektPunkt}: welcher Punkt abgehakt oder zurückgenommen wird. */
export interface PunktAenderung {
  punktId: number
  erledigt: boolean
}

/**
 * Hakt einen Punkt der Projekt-Checkliste ab oder nimmt den Haken zurück.
 *
 * Das Backend liefert den neuen Stand; er ersetzt die geladene Projektaufgabe.
 *
 * @param projektId - ID der Projektaufgabe.
 * @returns Mutation, die den neuen Stand liefert.
 */
export function useProjektPunkt(
  projektId: number,
): UseMutationResult<Projekt, Error, PunktAenderung> {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ punktId, erledigt }: PunktAenderung) =>
      apiAnfrage(`/api/projekte/${String(projektId)}/punkte/${String(punktId)}/`, projektSchema, {
        method: 'PUT',
        body: { erledigt },
      }),
    onSuccess: (projekt) => {
      queryClient.setQueryData(['projekt', projektId], projekt)
      return queryClient.invalidateQueries({ queryKey: FORTSCHRITT_SCHLUESSEL })
    },
  })
}

/**
 * Lädt das Dashboard (XP, Level, Statistik, Abzeichen, Meilensteine).
 *
 * Wird nach jeder Änderung des Fortschritts neu geladen, weil es denselben
 * Abfrage-Schlüssel-Anfang nutzt.
 *
 * @returns Abfrage-Zustand mit dem Dashboard.
 */
export function useDashboard(): UseQueryResult<Dashboard> {
  return useQuery({
    queryKey: [...FORTSCHRITT_SCHLUESSEL, 'dashboard'],
    queryFn: () => apiAnfrage('/api/dashboard/', dashboardSchema),
  })
}

/**
 * Lädt den Wochenplan samt Wochenauswertung.
 *
 * Gehört zum Fortschritt-Schlüssel, damit die Auswertung nach Änderungen neu lädt.
 *
 * @param woche - Ein Datum (JJJJ-MM-TT) der gewünschten Woche; `null` für die aktuelle.
 * @returns Abfrage-Zustand mit dem Wochenplan.
 */
export function useWochenplan(woche: string | null): UseQueryResult<Wochenplan> {
  return useQuery({
    queryKey: [...FORTSCHRITT_SCHLUESSEL, 'wochenplan', woche],
    queryFn: () =>
      apiAnfrage(
        woche === null ? '/api/wochenplan/' : `/api/wochenplan/?datum=${encodeURIComponent(woche)}`,
        wochenplanSchema,
      ),
  })
}
