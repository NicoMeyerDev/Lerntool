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
