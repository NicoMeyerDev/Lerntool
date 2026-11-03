/**
 * Fortschrittsbalken mit Beschriftung.
 */

/**
 * Zeigt, wie weit der Nutzer ist (z. B. Abschnitt 2 von 5).
 *
 * @param props.aktuell - Erreichter Wert.
 * @param props.gesamt - Gesamtwert (größer als 0).
 * @param props.beschriftung - Text für Screenreader und Anzeige.
 * @returns Einen zugänglichen Fortschrittsbalken.
 */
export function Fortschrittsbalken({
  aktuell,
  gesamt,
  beschriftung,
}: {
  aktuell: number
  gesamt: number
  beschriftung: string
}) {
  const prozent = gesamt > 0 ? Math.round((aktuell / gesamt) * 100) : 0
  return (
    <div>
      <div className="mb-1 flex justify-between text-sm text-text-muted">
        <span>{beschriftung}</span>
        <span>{prozent} %</span>
      </div>
      <div
        role="progressbar"
        aria-label={beschriftung}
        aria-valuemin={0}
        aria-valuemax={gesamt}
        aria-valuenow={aktuell}
        className="h-2 overflow-hidden rounded-full bg-surface-raised"
      >
        <div
          className="h-full rounded-full bg-linear-to-r from-accent-cyan to-accent-violet transition-[width] duration-300"
          style={{ width: `${String(prozent)}%` }}
        />
      </div>
    </div>
  )
}
