/**
 * Quiz am Ende eines Abschnitts: Fragen beantworten, abgeben, Auswertung ansehen.
 *
 * Die Oberfläche kennt die Lösung erst nach der Abgabe – die Auswertung kommt
 * vollständig vom Backend.
 */
import { useState, type SyntheticEvent } from 'react'

import { useQuiz, useQuizAbgabe } from '../api/lernen'
import type { Quiz, QuizErgebnis } from '../api/schemas'
import { Fehler, Laden } from './Zustand'

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
function ErgebnisKopf({ ergebnis }: { ergebnis: QuizErgebnis }) {
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
 * Formular mit den Fragen eines geladenen Quiz.
 *
 * @param props.quiz - Das Quiz ohne Lösung.
 * @returns Das Quiz-Formular samt Auswertung nach der Abgabe.
 */
function QuizFormular({ quiz }: { quiz: Quiz }) {
  const [auswahl, setAuswahl] = useState<Record<number, number>>({})
  const abgabe = useQuizAbgabe(quiz.id)
  const ergebnis = abgabe.data
  const alleBeantwortet = quiz.fragen.every((frage) => frage.id in auswahl)

  /** Schickt die gewählten Antworten an das Backend. */
  const abgeben = (event: SyntheticEvent) => {
    event.preventDefault()
    abgabe.mutate(
      Object.entries(auswahl).map(([frage, antwort]) => ({ frage: Number(frage), antwort })),
    )
  }

  /** Setzt das Quiz für einen neuen Versuch zurück. */
  const nochmal = () => {
    setAuswahl({})
    abgabe.reset()
  }

  return (
    <form onSubmit={abgeben} className="space-y-6">
      {ergebnis !== undefined && <ErgebnisKopf ergebnis={ergebnis} />}

      {quiz.fragen.map((frage, index) => {
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
                      setAuswahl((alt) => ({ ...alt, [frage.id]: antwort.id }))
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

      {abgabe.isError && <Fehler text={`Abgabe fehlgeschlagen: ${abgabe.error.message}`} />}

      {ergebnis === undefined ? (
        <div>
          <button
            type="submit"
            disabled={!alleBeantwortet || abgabe.isPending}
            className="min-h-12 w-full rounded-lg bg-accent-cyan px-6 font-bold text-bg disabled:cursor-not-allowed disabled:opacity-40 sm:w-auto"
          >
            {abgabe.isPending ? 'Wird ausgewertet …' : 'Antworten abgeben'}
          </button>
          {!alleBeantwortet && (
            <p className="mt-2 text-sm text-text-muted">Beantworte zuerst alle Fragen.</p>
          )}
        </div>
      ) : (
        <button
          type="button"
          onClick={nochmal}
          className="min-h-12 w-full rounded-lg border border-accent-cyan px-6 font-bold text-accent-cyan sm:w-auto"
        >
          Nochmal versuchen
        </button>
      )}
    </form>
  )
}

/**
 * Lädt ein Quiz und zeigt es an.
 *
 * @param props.quizId - ID des Quiz.
 * @returns Das Quiz, einen Ladehinweis oder eine Fehlermeldung.
 */
export function QuizAnsicht({ quizId }: { quizId: number }) {
  const quiz = useQuiz(quizId)
  return (
    <section
      aria-label="Quiz"
      className="rounded-card border border-border bg-surface p-5 shadow-lg shadow-black/30"
    >
      <h3 className="mb-4 text-sm font-semibold tracking-wide text-accent-cyan uppercase">Quiz</h3>
      {quiz.isPending && <Laden text="Quiz wird geladen …" />}
      {quiz.isError && <Fehler text="Das Quiz konnte nicht geladen werden." />}
      {quiz.isSuccess && <QuizFormular quiz={quiz.data} />}
    </section>
  )
}
