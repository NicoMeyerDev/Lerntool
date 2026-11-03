/**
 * Startseite nach der Anmeldung: Themen, Dashboard und Systemstatus.
 */
import { Link } from 'react-router'

import { useThemen } from '../api/lernen'
import { DashboardUebersicht } from '../components/DashboardUebersicht'
import { HealthStatus } from '../components/HealthStatus'
import { Fehler, Laden } from '../components/Zustand'

/**
 * Zeigt alle Themen als Karten, darunter das Dashboard und den Systemstatus.
 *
 * @returns Die Startseite.
 */
export function StartSeite() {
  const themen = useThemen()
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-extrabold">Deine Themen</h1>
      {themen.isPending && <Laden />}
      {themen.isError && <Fehler text="Die Themen konnten nicht geladen werden." />}
      {themen.isSuccess && themen.data.length === 0 && (
        <p className="text-text-muted">Noch keine Lerninhalte vorhanden.</p>
      )}
      {themen.isSuccess && (
        <ul className="grid gap-4 sm:grid-cols-2">
          {themen.data.map((thema) => (
            <li key={thema.id}>
              <Link
                to={`/themen/${thema.slug}`}
                className="block h-full rounded-card border border-border bg-surface p-5 transition-colors hover:border-accent-cyan"
              >
                <h2 className="text-xl font-bold">{thema.titel}</h2>
                {thema.beschreibung !== '' && (
                  <p className="mt-2 text-text-muted">{thema.beschreibung}</p>
                )}
              </Link>
            </li>
          ))}
        </ul>
      )}
      <DashboardUebersicht />
      <HealthStatus />
    </div>
  )
}
