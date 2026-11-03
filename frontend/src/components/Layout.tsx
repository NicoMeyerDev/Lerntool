/**
 * Rahmen für alle Seiten nach der Anmeldung: Kopfzeile mit Abmelden und Inhalt.
 */
import { Link, Navigate, Outlet } from 'react-router'

import { useAuth } from '../auth/kontext'

/**
 * Geschützter Bereich: ohne Anmeldung Weiterleitung zum Login, sonst Kopfzeile und Seite.
 *
 * @returns Das Layout mit der aktuellen Unterseite oder eine Weiterleitung.
 */
export function GeschuetzterBereich() {
  const { angemeldet, abmelden } = useAuth()
  if (!angemeldet) {
    return <Navigate to="/login" replace />
  }
  return (
    <div className="min-h-dvh">
      <header className="border-b border-border bg-surface/80">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-3">
          <Link
            to="/"
            className="inline-flex min-h-12 items-center bg-linear-to-r from-accent-cyan to-accent-violet bg-clip-text text-xl font-extrabold text-transparent"
          >
            Lerntool
          </Link>
          <Link
            to="/plan"
            className="inline-flex min-h-12 items-center rounded-lg px-4 text-text-muted hover:bg-surface-raised hover:text-text"
          >
            Plan
          </Link>
          <button
            type="button"
            onClick={() => void abmelden()}
            className="min-h-12 rounded-lg px-4 text-text-muted hover:bg-surface-raised hover:text-text"
          >
            Abmelden
          </button>
        </div>
      </header>
      <main className="mx-auto max-w-3xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}
