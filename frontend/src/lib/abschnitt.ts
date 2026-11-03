/**
 * Hilfsfunktionen für das Blättern durch die Abschnitte einer Lektion.
 */

/**
 * Liest die Abschnittsnummer (1-basiert) aus der URL und begrenzt sie auf gültige Werte.
 *
 * @param roh - Wert des URL-Parameters `abschnitt`.
 * @param anzahl - Anzahl der Abschnitte.
 * @returns Eine Nummer zwischen 1 und `anzahl` (bei 0 Abschnitten: 1).
 */
export function abschnittNummer(roh: string | null, anzahl: number): number {
  const zahl = Number(roh)
  if (!Number.isInteger(zahl) || zahl < 1) {
    return 1
  }
  return Math.min(zahl, Math.max(anzahl, 1))
}
