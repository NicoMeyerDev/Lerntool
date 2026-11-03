/**
 * Projektaufgabe: Aufgabe lesen, Checkliste abhaken, kurze Auswertung.
 *
 * Das Backend zählt und speichert die Haken; die Oberfläche zeigt nur den Stand.
 */
import { Link, useParams } from 'react-router'

import { useProjekt, useProjektPunkt } from '../api/lernen'
import type { Projekt } from '../api/schemas'
import { Fortschrittsbalken } from '../components/Fortschrittsbalken'
import { Markdown } from '../components/Markdown'
import { Fehler, Laden } from '../components/Zustand'
import { ladeFehlertext } from '../lib/fehler'

/**
 * Kurze Auswertung der Checkliste.
 *
 * @param props.projekt - Die Projektaufgabe mit Stand.
 * @returns Eine Rückmeldung, je nachdem wie weit der Nutzer ist.
 */
function Auswertung({ projekt }: { projekt: Projekt }) {
  if (projekt.abgeschlossen) {
    return (
      <p role="status" className="rounded-card border border-success/50 bg-success/10 p-4">
        <strong>Projekt abgeschlossen!</strong> Alle {projekt.gesamt} Punkte sind erledigt.
      </p>
    )
  }
  const offen = projekt.gesamt - projekt.erledigt
  return (
    <p role="status" className="rounded-card border border-border bg-surface p-4 text-text-muted">
      {projekt.erledigt === 0
        ? 'Noch nichts abgehakt. Fang mit dem ersten Punkt an.'
        : `Schon ${String(projekt.erledigt)} von ${String(projekt.gesamt)} erledigt – noch ${String(offen)} offen.`}
    </p>
  )
}

/**
 * Inhalt einer geladenen Projektaufgabe.
 *
 * @param props.projekt - Die Projektaufgabe mit Checkliste und Stand.
 * @returns Aufgabentext, Checkliste, Fortschritt und Auswertung.
 */
function ProjektInhalt({ projekt }: { projekt: Projekt }) {
  const aendern = useProjektPunkt(projekt.id)

  return (
    <div className="space-y-6">
      <article className="rounded-card border border-border bg-surface p-5">
        <Markdown text={projekt.beschreibung} />
      </article>

      <section aria-labelledby="checkliste" className="space-y-3">
        <h2 id="checkliste" className="text-xl font-bold text-accent-violet">
          Checkliste
        </h2>
        {projekt.punkte.length === 0 ? (
          <p className="text-text-muted">Diese Aufgabe hat noch keine Checkliste.</p>
        ) : (
          <>
            <Fortschrittsbalken
              aktuell={projekt.erledigt}
              gesamt={projekt.gesamt}
              beschriftung={`${String(projekt.erledigt)} von ${String(projekt.gesamt)} Punkten erledigt`}
            />
            <ul className="space-y-2">
              {projekt.punkte.map((punkt) => (
                <li key={punkt.id}>
                  <label className="flex min-h-12 cursor-pointer items-center gap-3 rounded-lg border border-border bg-surface px-4 py-2">
                    <input
                      type="checkbox"
                      checked={punkt.erledigt}
                      disabled={aendern.isPending}
                      onChange={(event) => {
                        aendern.mutate({ punktId: punkt.id, erledigt: event.target.checked })
                      }}
                      className="size-5 accent-accent-cyan"
                    />
                    <span className={punkt.erledigt ? 'text-text-muted line-through' : ''}>
                      {punkt.text}
                    </span>
                  </label>
                </li>
              ))}
            </ul>
            {aendern.isError && (
              <Fehler text={`Speichern fehlgeschlagen: ${aendern.error.message}`} />
            )}
            <Auswertung projekt={projekt} />
          </>
        )}
      </section>
    </div>
  )
}

/**
 * Lädt die Projektaufgabe aus der URL (`/projekte/:id`) und zeigt sie an.
 *
 * @returns Die Projektseite.
 */
export function ProjektSeite() {
  const { id } = useParams()
  const projektId = Number(id)
  const projekt = useProjekt(projektId)

  if (!Number.isInteger(projektId) || projektId < 1) {
    return <Fehler text="Ungültiges Projekt." />
  }
  if (projekt.isPending) {
    return <Laden />
  }
  if (projekt.isError) {
    return <Fehler text={ladeFehlertext(projekt.error, 'Das Projekt wurde nicht gefunden.')} />
  }
  return (
    <div className="space-y-4">
      <Link
        to="/"
        className="inline-flex min-h-12 items-center text-sm text-text-muted hover:text-accent-cyan"
      >
        ← Übersicht
      </Link>
      <h1 className="text-3xl font-extrabold">Projekt: {projekt.data.titel}</h1>
      <ProjektInhalt projekt={projekt.data} />
    </div>
  )
}
