/**
 * Basis für Aufrufe der REST-API des Backends.
 */

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
