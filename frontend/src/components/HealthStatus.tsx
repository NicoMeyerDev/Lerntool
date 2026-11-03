/**
 * Anzeige des Verbindungszustands zum Backend.
 */
import { useHealth } from '../api/health'

/** Darstellung eines Zustands: Text und Farbe des Statuspunkts. */
interface StatusAnzeige {
  text: string
  punktKlasse: string
}

/**
 * Zeigt an, ob API und Datenbank erreichbar sind.
 *
 * @returns Eine Karte mit farbigem Statuspunkt und Text.
 */
export function HealthStatus() {
  const { data, isPending, isError } = useHealth()

  let anzeige: StatusAnzeige
  if (isPending) {
    anzeige = { text: 'Verbindung wird geprüft …', punktKlasse: 'bg-warning' }
  } else if (isError) {
    anzeige = { text: 'Backend nicht erreichbar', punktKlasse: 'bg-danger' }
  } else if (data.status === 'ok') {
    anzeige = { text: 'Backend und Datenbank erreichbar', punktKlasse: 'bg-success' }
  } else {
    anzeige = { text: 'Backend erreichbar, Datenbank nicht', punktKlasse: 'bg-danger' }
  }

  return (
    <section
      aria-label="Systemstatus"
      className="rounded-card border border-border bg-surface p-5 shadow-lg shadow-black/30"
    >
      <h2 className="text-sm font-semibold tracking-wide text-text-muted uppercase">
        Systemstatus
      </h2>
      <p role="status" className="mt-3 flex items-center gap-3 text-lg">
        <span aria-hidden="true" className={`size-3 rounded-full ${anzeige.punktKlasse}`} />
        {anzeige.text}
      </p>
    </section>
  )
}
