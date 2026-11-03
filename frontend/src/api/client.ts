/**
 * Basis für Aufrufe der REST-API des Backends.
 */
import type { z } from 'zod'

import { leseToken, loescheToken } from '../auth/token'

/** Basis-URL der API. Leer bedeutet: gleicher Host (im Entwicklungsmodus über den Vite-Proxy). */
export const API_BASE_URL: string = import.meta.env.VITE_API_URL ?? ''

/**
 * Fehler bei einem API-Aufruf.
 */
export class ApiError extends Error {
  /** HTTP-Statuscode der Antwort oder `null`, wenn keine Antwort kam. */
  readonly status: number | null

  /**
   * Erzeugt einen API-Fehler.
   *
   * @param message - Beschreibung des Fehlers.
   * @param status - HTTP-Statuscode oder `null` bei Netzwerkfehlern.
   */
  constructor(message: string, status: number | null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

/**
 * Ruft einen API-Pfad per GET auf und liefert Statuscode und JSON-Inhalt.
 *
 * @param path - Pfad unterhalb der Basis-URL, z. B. `/api/health/`.
 * @returns Statuscode und geparster JSON-Inhalt (noch ungeprüft).
 * @throws {ApiError} Wenn keine Antwort kommt oder der Inhalt kein JSON ist.
 */
export async function getJson(path: string): Promise<{ status: number; body: unknown }> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { headers: { Accept: 'application/json' } })
  } catch (error) {
    console.error(`API nicht erreichbar: ${path}`, error)
    throw new ApiError('API nicht erreichbar', null)
  }

  try {
    const body: unknown = await response.json()
    return { status: response.status, body }
  } catch (error) {
    console.error(`Ungültige API-Antwort: ${path}`, error)
    throw new ApiError('Ungültige Antwort der API', response.status)
  }
}

/** Name des Browser-Ereignisses, wenn die API ein Token ablehnt (401). */
export const ABGEMELDET_EREIGNIS = 'lerntool:abgemeldet'

/** Optionen für {@link apiAnfrage}. */
export interface AnfrageOptionen {
  /** HTTP-Methode, Standard `GET`. */
  method?: 'GET' | 'POST'
  /** Inhalt, der als JSON gesendet wird. */
  body?: unknown
}

/**
 * Liest eine verständliche Fehlermeldung aus einer Fehlerantwort des Backends.
 *
 * @param body - Geparster Inhalt der Fehlerantwort.
 * @param status - HTTP-Statuscode.
 * @returns Die Meldung aus `detail` oder ein allgemeiner Text.
 */
function fehlertext(body: unknown, status: number): string {
  if (typeof body === 'object' && body !== null && 'detail' in body) {
    const detail = body.detail
    if (typeof detail === 'string') {
      return detail
    }
  }
  return `Anfrage fehlgeschlagen (Status ${String(status)})`
}

/**
 * Ruft die API mit dem gespeicherten Token auf und prüft die Antwort gegen ein Schema.
 *
 * Bei `401` wird das Token gelöscht und {@link ABGEMELDET_EREIGNIS} ausgelöst, damit
 * die App zur Anmeldung wechselt.
 *
 * @param path - Pfad unterhalb der Basis-URL, z. B. `/api/themen/`.
 * @param schema - zod-Schema, dem die Antwort entsprechen muss.
 * @param optionen - Methode und JSON-Inhalt.
 * @returns Die geprüfte Antwort.
 * @throws {ApiError} Bei Netzwerkfehlern, Fehlerstatus oder unerwarteter Antwort.
 */
export async function apiAnfrage<T>(
  path: string,
  schema: z.ZodType<T>,
  optionen: AnfrageOptionen = {},
): Promise<T> {
  const headers: Record<string, string> = { Accept: 'application/json' }
  const token = leseToken()
  if (token !== null) {
    headers.Authorization = `Token ${token}`
  }
  if (optionen.body !== undefined) {
    headers['Content-Type'] = 'application/json'
  }

  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: optionen.method ?? 'GET',
      headers,
      body: optionen.body === undefined ? undefined : JSON.stringify(optionen.body),
    })
  } catch (error) {
    console.error(`API nicht erreichbar: ${path}`, error)
    throw new ApiError('API nicht erreichbar', null)
  }

  if (response.status === 401) {
    loescheToken()
    window.dispatchEvent(new Event(ABGEMELDET_EREIGNIS))
    throw new ApiError('Nicht angemeldet', 401)
  }

  let body: unknown = undefined
  if (response.status !== 204) {
    try {
      body = await response.json()
    } catch (error) {
      console.error(`Ungültige API-Antwort: ${path}`, error)
      throw new ApiError('Ungültige Antwort der API', response.status)
    }
  }

  if (!response.ok) {
    throw new ApiError(fehlertext(body, response.status), response.status)
  }

  const geprueft = schema.safeParse(body)
  if (!geprueft.success) {
    console.error(`Antwort passt nicht zum Schema: ${path}`, geprueft.error)
    throw new ApiError('Unerwartete Antwort der API', response.status)
  }
  return geprueft.data
}
