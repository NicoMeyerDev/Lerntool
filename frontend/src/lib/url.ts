/**
 * Prüfung von Links, die aus der API kommen.
 */

/**
 * Prüft, ob ein Link gefahrlos als `href` gesetzt werden kann. Erlaubt sind nur
 * absolute `http:`- und `https:`-Adressen; `javascript:` und Ähnliches werden abgelehnt.
 *
 * @param url - Die zu prüfende Adresse.
 * @returns `true`, wenn die Adresse sicher ist.
 */
export function istSichereUrl(url: string): boolean {
  try {
    const protokoll = new URL(url).protocol
    return protokoll === 'http:' || protokoll === 'https:'
  } catch (error) {
    console.error(`Ungültige Adresse: ${url}`, error)
    return false
  }
}
