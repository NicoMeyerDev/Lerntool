/**
 * Anmeldeseite: Benutzername und Passwort eingeben.
 */
import { useState, type SyntheticEvent } from 'react'
import { Navigate } from 'react-router'

import { ApiError } from '../api/client'
import { useAuth } from '../auth/kontext'
import { Fehler } from '../components/Zustand'

/**
 * Übersetzt einen Anmeldefehler in eine verständliche Meldung.
 *
 * @param error - Der aufgetretene Fehler.
 * @returns Die Meldung für den Nutzer.
 */
function anmeldeFehlertext(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 400) {
      return 'Benutzername oder Passwort ist falsch.'
    }
    if (error.status === 429) {
      return 'Zu viele Versuche. Bitte warte eine Minute.'
    }
    if (error.status === null) {
      return 'Das Backend ist nicht erreichbar. Läuft der Server?'
    }
  }
  return 'Anmeldung fehlgeschlagen. Bitte versuche es erneut.'
}

/**
 * Login-Formular. Nach erfolgreicher Anmeldung geht es zur Startseite.
 *
 * @returns Die Anmeldeseite oder eine Weiterleitung, wenn bereits angemeldet.
 */
export function LoginSeite() {
  const { angemeldet, anmelden } = useAuth()
  const [benutzername, setBenutzername] = useState('')
  const [passwort, setPasswort] = useState('')
  const [fehler, setFehler] = useState<string | null>(null)
  const [laeuft, setLaeuft] = useState(false)

  if (angemeldet) {
    return <Navigate to="/" replace />
  }

  /** Sendet die Zugangsdaten und zeigt bei Fehlern eine Meldung. */
  const absenden = async (event: SyntheticEvent) => {
    event.preventDefault()
    setFehler(null)
    setLaeuft(true)
    try {
      await anmelden(benutzername, passwort)
    } catch (error) {
      console.error('Anmeldung fehlgeschlagen.', error)
      setFehler(anmeldeFehlertext(error))
    } finally {
      setLaeuft(false)
    }
  }

  const feldKlassen =
    'mt-1 min-h-12 w-full rounded-lg border border-border bg-bg px-4 text-text focus:border-accent-cyan focus:outline-none'

  return (
    <main className="mx-auto flex min-h-dvh max-w-sm flex-col justify-center px-4">
      <h1 className="bg-linear-to-r from-accent-cyan to-accent-violet bg-clip-text text-4xl font-extrabold text-transparent">
        Lerntool
      </h1>
      <p className="mt-2 mb-8 text-text-muted">Melde dich an, um weiterzulernen.</p>
      <form
        onSubmit={(event) => void absenden(event)}
        className="space-y-4 rounded-card border border-border bg-surface p-5"
      >
        <label className="block">
          <span className="text-sm text-text-muted">Benutzername</span>
          <input
            name="benutzername"
            autoComplete="username"
            required
            value={benutzername}
            onChange={(event) => {
              setBenutzername(event.target.value)
            }}
            className={feldKlassen}
          />
        </label>
        <label className="block">
          <span className="text-sm text-text-muted">Passwort</span>
          <input
            name="passwort"
            type="password"
            autoComplete="current-password"
            required
            value={passwort}
            onChange={(event) => {
              setPasswort(event.target.value)
            }}
            className={feldKlassen}
          />
        </label>
        {fehler !== null && <Fehler text={fehler} />}
        <button
          type="submit"
          disabled={laeuft}
          className="min-h-12 w-full rounded-lg bg-accent-cyan font-bold text-bg disabled:opacity-40"
        >
          {laeuft ? 'Anmelden …' : 'Anmelden'}
        </button>
      </form>
    </main>
  )
}
