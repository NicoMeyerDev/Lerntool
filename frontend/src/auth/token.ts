/**
 * Speichert das Login-Token im Browser (`localStorage`).
 *
 * Entscheidung und offene Sicherheitsfrage: siehe docs/ENTSCHEIDUNGEN.md (B2/B3)
 * und docs/OFFEN.md. Ist `localStorage` gesperrt (z. B. privater Modus), gilt der
 * Nutzer als abgemeldet, statt dass die App abstürzt.
 */

const SCHLUESSEL = 'lerntool.token'

/**
 * Liest das gespeicherte Token.
 *
 * @returns Das Token oder `null`, wenn keines gespeichert oder der Speicher gesperrt ist.
 */
export function leseToken(): string | null {
  try {
    return localStorage.getItem(SCHLUESSEL)
  } catch (error) {
    console.error('Token konnte nicht gelesen werden.', error)
    return null
  }
}

/**
 * Speichert ein Token.
 *
 * @param token - Das Token aus `/api/auth/login/`.
 */
export function speichereToken(token: string): void {
  try {
    localStorage.setItem(SCHLUESSEL, token)
  } catch (error) {
    console.error('Token konnte nicht gespeichert werden.', error)
  }
}

/**
 * Löscht das gespeicherte Token.
 */
export function loescheToken(): void {
  try {
    localStorage.removeItem(SCHLUESSEL)
  } catch (error) {
    console.error('Token konnte nicht gelöscht werden.', error)
  }
}
