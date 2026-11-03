/**
 * Verständliche Meldungen für fehlgeschlagene Ladevorgänge.
 */
import { ApiError } from '../api/client'

/**
 * Wählt die passende Meldung: „nicht gefunden“ nur bei Status 404, sonst ein allgemeiner
 * Ladefehler (Netzwerk, Serverfehler, unerwartete Antwort).
 *
 * @param error - Der aufgetretene Fehler.
 * @param nichtGefunden - Meldung für Status 404.
 * @returns Die anzuzeigende Meldung.
 */
export function ladeFehlertext(error: unknown, nichtGefunden: string): string {
  if (error instanceof ApiError && error.status === 404) {
    return nichtGefunden
  }
  return 'Laden fehlgeschlagen. Bitte versuche es später noch einmal.'
}
