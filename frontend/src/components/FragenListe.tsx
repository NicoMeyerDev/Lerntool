/**
 * Gemeinsame Darstellung von Fragen mit Antwortmöglichkeiten und deren Auswertung.
 * Wird vom Quiz (nach jedem Abschnitt) und vom Test (nach jedem Themenfeld) genutzt.
 *
 * Die Oberfläche kennt die Lösung erst nach der Abgabe – die Auswertung kommt
 * vollständig vom Backend.
 */
import type { Quiz, QuizErgebnis } from '../api/schemas'

/** Zustand einer Antwortmöglichkeit nach der Auswertung. */
type Markierung = 'richtig' | 'falsch-gewaehlt' | 'neutral'

/**
 * Bestimmt die Markierung einer Antwort für die Auswertung.
 *
 * @param antwortId - Die angezeigte Antwort.
 * @param auswertung - Auswertung der zugehörigen Frage oder `undefined` vor der Abgabe.
 * @returns Wie die Antwort hervorgehoben wird.
 */
function markierung(
  antwortId: number,
  auswertung: QuizErgebnis['fragen'][number] | undefined,
): Markierung {
  if (auswertung === undefined) {
    return 'neutral'
  }
  if (antwortId === auswertung.richtige_antwort_id) {
    return 'richtig'
  }
  if (antwortId === auswertung.gewaehlte_antwort_id) {
    return 'falsch-gewaehlt'
  }
  return 'neutral'
}

/** Tailwind-Klassen je Markierung. */
const MARKIERUNGS_KLASSEN: Record<Markierung, string> = {
  richtig: 'border-success bg-success/10',
  'falsch-gewaehlt': 'border-danger bg-danger/10',
  neutral: 'border-border bg-surface',
}

/**
 * Zusammenfassung der Auswertung: Punkte, Bestwert und eine kurze Rückmeldung.
 *
 * @param props.ergebnis - Die Auswertung vom Backend.
 * @returns Eine hervorgehobene Ergebnis-Karte.
 */
export function ErgebnisKopf({ ergebnis }: { ergebnis: QuizErgebnis }) {
  const alleRichtig = ergebnis.punkte === ergebnis.max_punkte
  return (
    <div
      role="status"
      className="rounded-card border border-accent-violet/50 bg-accent-violet/10 p-4"
    >
      <p className="text-2xl font-bold">
        {ergebnis.punkte} von {ergebnis.max_punkte} richtig
      </p>
      <p className="mt-1 text-text-muted">
        {alleRichtig
          ? 'Stark – alles richtig!'
          : 'Schau dir unten die Erklärungen an und versuch es noch einmal.'}{' '}
        Bestwert: {ergebnis.bestwert} von {ergebnis.max_punkte}.
      </p>
    </div>
  )
}

/**
 * Die Fragen eines Quiz oder Tests als Auswahlfelder.
 *
 * @param props.fragen - Fragen ohne Lösung.
 * @param props.auswahl - Bisher gewählte Antworten (Frage-ID → Antwort-ID).
 * @param props.onWaehle - Wird aufgerufen, wenn eine Antwort gewählt wird.
 * @param props.ergebnis - Auswertung nach der Abgabe; dann sind die Felder gesperrt.
 * @returns Eine Gruppe je Frage, nach der Abgabe mit Markierung und Erklärung.
 */
export function FragenListe({
  fragen,
  auswahl,
  onWaehle,
  ergebnis,
}: {
  fragen: Quiz['fragen']
  auswahl: Record<number, number>
  onWaehle: (frageId: number, antwortId: number) => void
  ergebnis: QuizErgebnis | undefined
}) {
  return (
    <>
      {fragen.map((frage, index) => {
        const auswertung = ergebnis?.fragen.find((f) => f.frage_id === frage.id)
        return (
          <fieldset key={frage.id} className="space-y-2">
            <legend className="mb-2 font-semibold">
              {index + 1}. {frage.text}
            </legend>
            {frage.antworten.map((antwort) => {
              const art = markierung(antwort.id, auswertung)
              return (
                <label
                  key={antwort.id}
                  className={`flex min-h-12 cursor-pointer items-center gap-3 rounded-lg border px-4 py-2 ${MARKIERUNGS_KLASSEN[art]}`}
                >
                  <input
                    type="radio"
                    name={`frage-${String(frage.id)}`}
                    value={antwort.id}
                    checked={auswahl[frage.id] === antwort.id}
                    disabled={ergebnis !== undefined}
                    onChange={() => {
                      onWaehle(frage.id, antwort.id)
                    }}
                    className="size-5 accent-accent-cyan"
                  />
                  <span className="flex-1">{antwort.text}</span>
                  {art === 'richtig' && <span className="text-sm text-success">✓ richtig</span>}
                  {art === 'falsch-gewaehlt' && (
                    <span className="text-sm text-danger">✗ deine Antwort</span>
                  )}
                </label>
              )
            })}
            {auswertung !== undefined && auswertung.erklaerung !== '' && (
              <p className="rounded-lg bg-surface-raised p-3 text-sm text-text-muted">
                <span className="font-semibold text-text">Erklärung: </span>
                {auswertung.erklaerung}
              </p>
            )}
          </fieldset>
        )
      })}
    </>
  )
}
