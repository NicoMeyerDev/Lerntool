/**
 * Hilfsfunktionen für Zeitangaben im Test.
 */

/**
 * Formatiert Sekunden als „mm:ss“ (z. B. 1800 → „30:00“).
 *
 * @param sekunden - Anzahl Sekunden; negative Werte zählen als 0.
 * @returns Minuten und Sekunden, jeweils zweistellig.
 */
export function formatiereRestzeit(sekunden: number): string {
  const gesamt = Math.max(0, Math.floor(sekunden))
  const minuten = Math.floor(gesamt / 60)
  const rest = gesamt % 60
  return `${String(minuten).padStart(2, '0')}:${String(rest).padStart(2, '0')}`
}

/**
 * Formatiert ein ISO-Datum als „TT.MM.JJJJ“ (z. B. 2026-11-04 → „04.11.2026“).
 *
 * @param iso - Datum im Format JJJJ-MM-TT.
 * @returns Das deutsche Datum; bei unerwartetem Format der unveränderte Text.
 */
export function formatiereDatum(iso: string): string {
  const treffer = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso)
  return treffer ? `${treffer[3]}.${treffer[2]}.${treffer[1]}` : iso
}
