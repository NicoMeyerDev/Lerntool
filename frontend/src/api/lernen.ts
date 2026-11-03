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
  fortschrittListeSchema,
  fortschrittSchema,
  lektionSchema,
  quizErgebnisSchema,
  quizSchema,
  themaDetailSchema,
  themenSchema,
  type Fortschritt,
  type Lektion,
  type Quiz,
  type QuizErgebnis,
  type Thema,
  type ThemaDetail,
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
