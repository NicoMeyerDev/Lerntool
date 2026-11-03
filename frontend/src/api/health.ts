/**
 * Zugriff auf den Health-Check `/api/health/` des Backends.
 */
import { useQuery, type UseQueryResult } from '@tanstack/react-query'

import { ApiError, getJson } from './client'

/** Antwort des Health-Checks, wie das Backend sie liefert. */
export interface HealthResponse {
  status: 'ok' | 'fehler'
  datenbank: string
}

/**
 * Prüft, ob ein unbekannter Wert die Form einer Health-Antwort hat.
 *
 * @param value - Der zu prüfende Wert.
 * @returns `true`, wenn `value` eine gültige {@link HealthResponse} ist.
 */
export function isHealthResponse(value: unknown): value is HealthResponse {
  if (typeof value !== 'object' || value === null) {
    return false
  }
  const record = value as Record<string, unknown>
  return (
    (record.status === 'ok' || record.status === 'fehler') && typeof record.datenbank === 'string'
  )
}

/**
 * Ruft den Health-Check ab.
 *
 * Auch die Antwort 503 (Datenbank nicht erreichbar) wird als Ergebnis geliefert,
 * damit die Oberfläche den genauen Zustand anzeigen kann.
 *
 * @returns Die Health-Antwort des Backends.
 * @throws {ApiError} Wenn die API nicht antwortet oder die Antwort unerwartet ist.
 */
export async function fetchHealth(): Promise<HealthResponse> {
  const { status, body } = await getJson('/api/health/')
  if ((status === 200 || status === 503) && isHealthResponse(body)) {
    return body
  }
  console.error('Unerwartete Antwort vom Health-Check', status, body)
  throw new ApiError('Unerwartete Antwort vom Health-Check', status)
}

/**
 * React-Hook für den Health-Check.
 *
 * @returns Abfrage-Zustand von TanStack Query mit der Health-Antwort.
 */
export function useHealth(): UseQueryResult<HealthResponse> {
  return useQuery({ queryKey: ['health'], queryFn: fetchHealth, retry: false })
}
