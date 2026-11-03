/**
 * Wochen- und Tagesplan: feste Blöcke für fünf Lerntage und die Wochenauswertung.
 * Alle Inhalte und Zahlen kommen vom Backend; hier wird nur dargestellt und geblättert.
 */
import { Link, useSearchParams } from 'react-router'

import { useWochenplan } from '../api/lernen'
import type { Wochenplan } from '../api/schemas'
import { Fehler, Laden } from '../components/Zustand'
import { formatiereDatum } from '../lib/zeit'

/**
 * Ein Lerntag mit seinen Blöcken.
 *
 * @param props.tag - Der Tag aus dem Wochenplan.
 * @returns Die Tageskarte; der heutige Tag ist hervorgehoben.
 */
function Tageskarte({ tag }: { tag: Wochenplan['tage'][number] }) {
  return (
    <li
      aria-current={tag.ist_heute ? 'date' : undefined}
      className={`rounded-card border p-4 ${
        tag.ist_heute ? 'border-accent-cyan bg-accent-cyan/10' : 'border-border bg-surface'
      }`}
    >
      <h3 className="text-lg font-bold">
        {tag.wochentag}, {formatiereDatum(tag.datum)}
        {tag.ist_heute && <span className="ml-2 text-sm text-accent-cyan">Heute</span>}
      </h3>
      <ul className="mt-3 space-y-3">
        {tag.bloecke.map((block) => (
          <li key={block.schluessel} className="border-l-4 border-accent-violet pl-3">
            <p className="font-semibold">
              {block.titel}{' '}
              <span className="text-sm font-normal text-text-muted">
                ({block.tageszeit === 'vormittag' ? 'Vormittag' : 'Nachmittag'}, {block.dauer})
              </span>
            </p>
            <p className="text-text-muted">{block.beschreibung}</p>
          </li>
        ))}
      </ul>
    </li>
  )
}

/**
 * Die Wochenauswertung als Liste von Kennzahlen.
 *
 * @param props.auswertung - Die Zahlen der Woche.
 * @returns Die Auswertung.
 */
function Auswertung({ auswertung }: { auswertung: Wochenplan['auswertung'] }) {
  const zeilen: [string, number][] = [
    ['Abschnitte gelesen', auswertung.abschnitte_gelesen],
    ['Quizze bearbeitet', auswertung.quizze_bearbeitet],
    ['Tests bearbeitet', auswertung.tests_bearbeitet],
    ['Projekte erledigt', auswertung.projekte_erledigt],
  ]
  return (
    <section aria-labelledby="wochenauswertung" className="space-y-3">
      <h2 id="wochenauswertung" className="text-xl font-bold text-accent-violet">
        Wochenauswertung
      </h2>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {zeilen.map(([beschriftung, wert]) => (
          <div key={beschriftung} className="rounded-card border border-border bg-surface p-4">
            <p className="text-2xl font-extrabold text-accent-cyan">{wert}</p>
            <p className="mt-1 text-sm text-text-muted">{beschriftung}</p>
          </div>
        ))}
      </div>
      <p className="text-text-muted">
        Trefferquote der Woche:{' '}
        <strong className="text-text">
          {auswertung.trefferquote_prozent === null
            ? 'noch kein Ergebnis'
            : `${String(auswertung.trefferquote_prozent)} %`}
        </strong>
      </p>
      <p className="text-sm text-text-muted">
        Hinweis: Ein Eintrag zählt in der Woche, in der du ihn zuletzt bearbeitet hast.
      </p>
    </section>
  )
}

/**
 * Seite „Wochenplan“. Die Woche steht in der Adresse (`?woche=JJJJ-MM-TT`), so
 * funktionieren Zurück-Taste und Neuladen.
 *
 * @returns Wochenplan mit Blättern zur Vor- und Folgewoche.
 */
export function PlanSeite() {
  const [parameter] = useSearchParams()
  const plan = useWochenplan(parameter.get('woche'))
  const knopf =
    'inline-flex min-h-12 items-center rounded-lg border border-border px-4 hover:border-accent-cyan'
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-extrabold">Wochenplan</h1>
      {plan.isPending && <Laden text="Plan wird geladen …" />}
      {plan.isError && <Fehler text="Der Plan konnte nicht geladen werden." />}
      {plan.isSuccess && (
        <>
          <nav aria-label="Woche wählen" className="flex items-center justify-between gap-2">
            <Link to={`/plan?woche=${plan.data.vorherige_woche}`} className={knopf}>
              ← Vorwoche
            </Link>
            <p className="text-center font-semibold">
              {formatiereDatum(plan.data.woche_start)} – {formatiereDatum(plan.data.woche_ende)}
            </p>
            <Link to={`/plan?woche=${plan.data.naechste_woche}`} className={knopf}>
              Folgewoche →
            </Link>
          </nav>
          {!plan.data.ist_aktuelle_woche && (
            <Link to="/plan" className="inline-block text-accent-cyan underline">
              Zur aktuellen Woche
            </Link>
          )}
          <ul className="space-y-4">
            {plan.data.tage.map((tag) => (
              <Tageskarte key={tag.datum} tag={tag} />
            ))}
          </ul>
          <Auswertung auswertung={plan.data.auswertung} />
        </>
      )}
    </div>
  )
}
