/**
 * React-Kontext für den Anmeldezustand und der Hook, um ihn zu lesen.
 */
import { createContext, useContext } from 'react'

/** Was der Anmelde-Kontext bereitstellt. */
export interface AuthWert {
  /** Ob ein Token vorhanden ist. */
  angemeldet: boolean
  /**
   * Meldet mit Benutzername und Passwort an und speichert das Token.
   *
   * @throws {ApiError} Bei falschen Zugangsdaten (400), zu vielen Versuchen (429) oder Netzfehlern.
   */
  anmelden: (benutzername: string, passwort: string) => Promise<void>
  /** Meldet ab: Token beim Backend ungültig machen und lokal löschen. */
  abmelden: () => Promise<void>
}

export const AuthKontext = createContext<AuthWert | null>(null)

/**
 * Liefert den Anmeldezustand.
 *
 * @returns Den Wert des {@link AuthKontext}.
 * @throws {Error} Wenn die Komponente nicht innerhalb von `AuthProvider` steht.
 */
export function useAuth(): AuthWert {
  const wert = useContext(AuthKontext)
  if (wert === null) {
    throw new Error('useAuth muss innerhalb von <AuthProvider> verwendet werden.')
  }
  return wert
}
