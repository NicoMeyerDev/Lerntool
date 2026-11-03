/**
 * Lektion lesen: ein Abschnitt nach dem anderen, jeweils mit Quiz, am Ende die Quellen.
 */
import { Link, useParams, useSearchParams } from 'react-router'

import { useAbschnittGelesen, useFortschritt, useLektion } from '../api/lernen'
import type { Lektion } from '../api/schemas'
import { Fortschrittsbalken } from '../components/Fortschrittsbalken'
import { Markdown } from '../components/Markdown'
import { QuizAnsicht } from '../components/QuizAnsicht'
import { Fehler, Laden } from '../components/Zustand'
import { abschnittNummer } from '../lib/abschnitt'
import { ladeFehlertext } from '../lib/fehler'
import { istSichereUrl } from '../lib/url'

/**
 * Inhalt einer geladenen Lektion mit Blättern zwischen den Abschnitten.
 *
 * @param props.lektion - Die Lektion.
 * @returns Abschnitt, Quiz, Navigation und Quellen.
 */
function LektionInhalt({ lektion }: { lektion: Lektion }) {
  const [parameter, setParameter] = useSearchParams()
  const fortschritt = useFortschritt()
  const gelesen = useAbschnittGelesen()

  const anzahl = lektion.abschnitte.length
  if (anzahl === 0) {
    return <p className="text-text-muted">Diese Lektion hat noch keine Abschnitte.</p>
  }

  const nummer = abschnittNummer(parameter.get('abschnitt'), anzahl)
  const abschnitt = lektion.abschnitte[nummer - 1]
  const istLetzter = nummer === anzahl
  const gelesenIds = new Set(fortschritt.data?.map((eintrag) => eintrag.abschnitt) ?? [])
  const anzahlGelesen = lektion.abschnitte.filter((a) => gelesenIds.has(a.id)).length

  /**
   * Wechselt zu einem anderen Abschnitt.
   *
   * @param ziel - Nummer des Abschnitts (1-basiert).
   */
  const gehe = (ziel: number) => {
    setParameter({ abschnitt: String(ziel) })
    window.scrollTo({ top: 0 })
  }

  /** Markiert den aktuellen Abschnitt als gelesen und geht ggf. weiter. */
  const abschliessen = () => {
    gelesen.mutate(abschnitt.id, {
      onSuccess: () => {
        if (!istLetzter) {
          gehe(nummer + 1)
        }
      },
    })
  }

  const fertig = istLetzter && gelesenIds.has(abschnitt.id)
  const knopf = 'min-h-12 rounded-lg px-5 font-bold disabled:cursor-not-allowed disabled:opacity-40'

  return (
    <div className="space-y-6">
      <Fortschrittsbalken
        aktuell={anzahlGelesen}
        gesamt={anzahl}
        beschriftung={`${String(anzahlGelesen)} von ${String(anzahl)} Abschnitten gelesen`}
      />

      <article className="rounded-card border border-border bg-surface p-5">
        <p className="text-sm text-text-muted">
          Abschnitt {nummer} von {anzahl}
          {gelesenIds.has(abschnitt.id) && <span className="ml-2 text-success">✓ gelesen</span>}
        </p>
        <h2 className="mt-1 text-2xl font-bold">{abschnitt.titel}</h2>
        <Markdown text={abschnitt.inhalt} />
      </article>

      {abschnitt.quiz_id !== null && (
        <QuizAnsicht key={abschnitt.quiz_id} quizId={abschnitt.quiz_id} />
      )}

      {gelesen.isError && <Fehler text="Der Fortschritt konnte nicht gespeichert werden." />}

      <nav aria-label="Abschnitte" className="flex flex-wrap justify-between gap-3">
        <button
          type="button"
          onClick={() => {
            gehe(nummer - 1)
          }}
          disabled={nummer === 1}
          className={`${knopf} border border-border text-text`}
        >
          ← Zurück
        </button>
        <button
          type="button"
          onClick={abschliessen}
          disabled={gelesen.isPending}
          className={`${knopf} bg-accent-cyan text-bg`}
        >
          {istLetzter ? 'Lektion abschließen' : 'Gelesen – weiter →'}
        </button>
      </nav>

      {fertig && (
        <p role="status" className="rounded-card border border-success/50 bg-success/10 p-4">
          Lektion abgeschlossen. Gut gemacht!
        </p>
      )}

      {lektion.quellen.length > 0 && (
        <section aria-labelledby="quellen" className="border-t border-border pt-4 text-sm">
          <h2 id="quellen" className="font-semibold text-text-muted">
            Quellen
          </h2>
          <ul className="mt-2 space-y-1">
            {lektion.quellen.map((quelle) => (
              <li key={quelle.url}>
                {istSichereUrl(quelle.url) ? (
                  <a
                    href={quelle.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex min-h-12 items-center text-accent-cyan underline underline-offset-2"
                  >
                    {quelle.titel}
                  </a>
                ) : (
                  // Unsichere Adressen nur als Text zeigen, nie als Link.
                  <span>{quelle.titel}</span>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  )
}

/**
 * Lädt die Lektion aus der URL (`/lektionen/:id`) und zeigt sie an.
 *
 * @returns Die Lektionsseite.
 */
export function LektionSeite() {
  const { id } = useParams()
  const lektionId = Number(id)
  const lektion = useLektion(lektionId)

  if (!Number.isInteger(lektionId) || lektionId < 1) {
    return <Fehler text="Ungültige Lektion." />
  }
  if (lektion.isPending) {
    return <Laden />
  }
  if (lektion.isError) {
    return <Fehler text={ladeFehlertext(lektion.error, 'Die Lektion wurde nicht gefunden.')} />
  }
  return (
    <div className="space-y-4">
      <Link
        to="/"
        className="inline-flex min-h-12 items-center text-sm text-text-muted hover:text-accent-cyan"
      >
        ← Übersicht
      </Link>
      <h1 className="text-3xl font-extrabold">{lektion.data.titel}</h1>
      <LektionInhalt lektion={lektion.data} />
    </div>
  )
}
