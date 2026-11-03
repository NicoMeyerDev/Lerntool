/**
 * Gliederung eines Themas: Phasen mit ihren Lektionen und Projektaufgaben.
 */
import { Link, useParams } from 'react-router'

import { useThema } from '../api/lernen'
import { Fehler, Laden } from '../components/Zustand'
import { ladeFehlertext } from '../lib/fehler'

/**
 * Zeigt die Phasen eines Themas; jede Lektion ist ein Link zur Lektionsseite.
 *
 * @returns Die Themenseite.
 */
export function ThemaSeite() {
  const { slug = '' } = useParams()
  const thema = useThema(slug)

  if (thema.isPending) {
    return <Laden />
  }
  if (thema.isError) {
    return <Fehler text={ladeFehlertext(thema.error, 'Das Thema wurde nicht gefunden.')} />
  }

  return (
    <div className="space-y-8">
      <div>
        <Link
          to="/"
          className="inline-flex min-h-12 items-center text-sm text-text-muted hover:text-accent-cyan"
        >
          ← Alle Themen
        </Link>
        <h1 className="mt-2 text-3xl font-extrabold">{thema.data.titel}</h1>
        {thema.data.beschreibung !== '' && (
          <p className="mt-2 text-text-muted">{thema.data.beschreibung}</p>
        )}
      </div>

      {thema.data.phasen.map((phase) => (
        <section key={phase.id} aria-labelledby={`phase-${String(phase.id)}`}>
          <h2 id={`phase-${String(phase.id)}`} className="text-xl font-bold text-accent-violet">
            Phase {phase.reihenfolge}: {phase.titel}
          </h2>
          {phase.beschreibung !== '' && (
            <p className="mt-1 text-text-muted">{phase.beschreibung}</p>
          )}
          <ol className="mt-3 space-y-2">
            {phase.lektionen.map((lektion) => (
              <li key={lektion.id}>
                <Link
                  to={`/lektionen/${String(lektion.id)}`}
                  className="flex min-h-12 items-center rounded-lg border border-border bg-surface px-4 py-3 hover:border-accent-cyan"
                >
                  <span className="font-semibold">{lektion.titel}</span>
                </Link>
              </li>
            ))}
          </ol>
          {phase.projektaufgaben.length > 0 && (
            <ul aria-label="Projekte" className="mt-3 space-y-2">
              {phase.projektaufgaben.map((projekt) => (
                <li key={projekt.id}>
                  <Link
                    to={`/projekte/${String(projekt.id)}`}
                    className="flex min-h-12 items-center rounded-lg border border-accent-violet/50 bg-surface px-4 py-3 hover:border-accent-violet"
                  >
                    <span className="font-semibold">Projekt: {projekt.titel}</span>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </section>
      ))}
    </div>
  )
}
