/**
 * Quiz am Ende eines Abschnitts: Fragen beantworten, abgeben, Auswertung ansehen.
 *
 * Die Oberfläche kennt die Lösung erst nach der Abgabe – die Auswertung kommt
 * vollständig vom Backend.
 */
import { useState, type SyntheticEvent } from 'react'

import { useQuiz, useQuizAbgabe } from '../api/lernen'
import type { Quiz } from '../api/schemas'
import { ErgebnisKopf, FragenListe } from './FragenListe'
import { Fehler, Laden } from './Zustand'

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

      <FragenListe
        fragen={quiz.fragen}
        auswahl={auswahl}
        onWaehle={(frageId, antwortId) => {
          setAuswahl((alt) => ({ ...alt, [frageId]: antwortId }))
        }}
        ergebnis={ergebnis}
      />

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
