/**
 * Test nach einem Themenfeld: Zeitlimit (höchstens 30 Minuten), abgeben, Auswertung.
 *
 * Die Zeit läuft auf dem Server. Die Oberfläche zählt nur die vom Server gemeldete
 * Restzeit herunter und gibt bei Ablauf automatisch ab. Prüfung und Auswertung
 * macht das Backend.
 */
import { useEffect, useRef, useState, type SyntheticEvent } from 'react'
import { Link, useParams } from 'react-router'

import { useTest, useTestAbgabe, useTestStart } from '../api/lernen'
import type { TestAufgabe } from '../api/schemas'
import { ErgebnisKopf, FragenListe } from '../components/FragenListe'
import { Fehler, Laden } from '../components/Zustand'
import { ladeFehlertext } from '../lib/fehler'
import { useCountdown } from '../lib/useCountdown'
import { formatiereRestzeit } from '../lib/zeit'

/** Ab dieser Restzeit (Sekunden) wird die Uhr als Warnung hervorgehoben. */
const WARN_SEKUNDEN = 5 * 60

/**
 * Laufender Testversuch mit Uhr, Fragen und Abgabe.
 *
 * @param props.test - Der Test ohne Lösung.
 * @param props.sekundenRest - Restzeit laut Server beim Start.
 * @param props.onNeuStarten - Wird aufgerufen, wenn der Nutzer einen neuen Versuch will.
 * @returns Uhr, Fragen und nach der Abgabe die Auswertung.
 */
function TestLauf({
  test,
  sekundenRest,
  onNeuStarten,
}: {
  test: TestAufgabe
  sekundenRest: number
  onNeuStarten: () => void
}) {
  const [auswahl, setAuswahl] = useState<Record<number, number>>({})
  const abgabe = useTestAbgabe(test.id)
  const ergebnis = abgabe.data
  const auswahlRef = useRef(auswahl)
  const automatischAbgegeben = useRef(false)

  useEffect(() => {
    auswahlRef.current = auswahl
  })

  /**
   * Schickt die gewählten Antworten an das Backend.
   *
   * @param antworten - Auswahl (Frage-ID → Antwort-ID).
   */
  const sende = (antworten: Record<number, number>) => {
    abgabe.mutate(
      Object.entries(antworten).map(([frage, antwort]) => ({ frage: Number(frage), antwort })),
    )
  }

  const rest = useCountdown(sekundenRest, () => {
    // Zeit ist um: einmal automatisch mit dem aktuellen Stand abgeben.
    if (!automatischAbgegeben.current && abgabe.isIdle) {
      automatischAbgegeben.current = true
      sende(auswahlRef.current)
    }
  })

  const abgeben = (event: SyntheticEvent) => {
    event.preventDefault()
    sende(auswahl)
  }

  const beantwortet = Object.keys(auswahl).length
  const gesperrt = abgabe.isPending || ergebnis !== undefined

  return (
    <form onSubmit={abgeben} className="space-y-6">
      {ergebnis === undefined && (
        <div
          role="timer"
          aria-label="Verbleibende Zeit"
          className={`sticky top-0 z-10 rounded-card border p-3 text-center font-mono text-2xl font-bold ${
            rest <= WARN_SEKUNDEN
              ? 'border-danger bg-bg text-danger'
              : 'border-accent-cyan/50 bg-bg text-accent-cyan'
          }`}
        >
          {formatiereRestzeit(rest)}
        </div>
      )}

      {ergebnis !== undefined && <ErgebnisKopf ergebnis={ergebnis} />}

      <FragenListe
        fragen={test.fragen}
        auswahl={auswahl}
        onWaehle={(frageId, antwortId) => {
          setAuswahl((alt) => ({ ...alt, [frageId]: antwortId }))
        }}
        ergebnis={ergebnis}
      />

      {abgabe.isError && <Fehler text={`Abgabe fehlgeschlagen: ${abgabe.error.message}`} />}

      {ergebnis === undefined ? (
        <div className="space-y-2">
          <button
            type="submit"
            disabled={gesperrt}
            className="min-h-12 w-full rounded-lg bg-accent-cyan px-6 font-bold text-bg disabled:cursor-not-allowed disabled:opacity-40 sm:w-auto"
          >
            {abgabe.isPending ? 'Wird ausgewertet …' : 'Test abgeben'}
          </button>
          <p className="text-sm text-text-muted">
            {beantwortet} von {test.fragen.length} Fragen beantwortet. Unbeantwortete Fragen zählen
            als falsch.
          </p>
          {abgabe.isError && (
            <button
              type="button"
              onClick={onNeuStarten}
              className="min-h-12 rounded-lg border border-accent-cyan px-6 font-bold text-accent-cyan"
            >
              Neuen Versuch starten
            </button>
          )}
        </div>
      ) : (
        <button
          type="button"
          onClick={onNeuStarten}
          className="min-h-12 w-full rounded-lg border border-accent-cyan px-6 font-bold text-accent-cyan sm:w-auto"
        >
          Nochmal versuchen
        </button>
      )}
    </form>
  )
}

/**
 * Startbildschirm und laufender Versuch eines geladenen Tests.
 *
 * @param props.test - Der Test ohne Lösung.
 * @returns Entweder den Hinweis mit Startknopf oder den laufenden Versuch.
 */
function TestInhalt({ test }: { test: TestAufgabe }) {
  const start = useTestStart(test.id)

  if (test.fragen.length === 0) {
    return <p className="text-text-muted">Dieser Test hat noch keine Fragen.</p>
  }

  if (start.data === undefined) {
    return (
      <div className="space-y-4 rounded-card border border-border bg-surface p-5">
        <p>
          Dieser Test hat <strong>{test.fragen.length} Fragen</strong> und dauert höchstens{' '}
          <strong>{test.zeitlimit_minuten} Minuten</strong>. Die Zeit läuft ab dem Start weiter,
          auch wenn du die Seite neu lädst – deine gewählten Antworten gehen dabei aber verloren.
          Läuft die Zeit ab, wird automatisch abgegeben.
        </p>
        {start.isError && <Fehler text={`Start fehlgeschlagen: ${start.error.message}`} />}
        <button
          type="button"
          onClick={() => {
            start.mutate()
          }}
          disabled={start.isPending}
          className="min-h-12 w-full rounded-lg bg-accent-cyan px-6 font-bold text-bg disabled:cursor-not-allowed disabled:opacity-40 sm:w-auto"
        >
          {start.isPending ? 'Wird gestartet …' : 'Test starten'}
        </button>
      </div>
    )
  }

  return (
    <TestLauf
      // Neuer Versuch → neu mounten, damit Antworten und Uhr frisch beginnen.
      key={start.data.versuch_id}
      test={test}
      sekundenRest={start.data.sekunden_rest}
      onNeuStarten={() => {
        start.reset()
      }}
    />
  )
}

/**
 * Lädt den Test aus der URL (`/tests/:id`) und zeigt ihn an.
 *
 * @returns Die Testseite.
 */
export function TestSeite() {
  const { id } = useParams()
  const testId = Number(id)
  const test = useTest(testId)

  if (!Number.isInteger(testId) || testId < 1) {
    return <Fehler text="Ungültiger Test." />
  }
  if (test.isPending) {
    return <Laden text="Test wird geladen …" />
  }
  if (test.isError) {
    return <Fehler text={ladeFehlertext(test.error, 'Der Test wurde nicht gefunden.')} />
  }
  return (
    <div className="space-y-4">
      <Link
        to={`/lektionen/${String(test.data.lektion)}`}
        className="inline-flex min-h-12 items-center text-sm text-text-muted hover:text-accent-cyan"
      >
        ← Zur Lektion
      </Link>
      <h1 className="text-3xl font-extrabold">Test</h1>
      <TestInhalt test={test.data} />
    </div>
  )
}
