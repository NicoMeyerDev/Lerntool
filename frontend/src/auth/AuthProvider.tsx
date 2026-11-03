/**
 * Stellt den Anmeldezustand für die ganze App bereit.
 */
import { useQueryClient } from '@tanstack/react-query'
import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'

import { ABGEMELDET_EREIGNIS, apiAnfrage } from '../api/client'
import { leerSchema, tokenSchema } from '../api/schemas'
import { AuthKontext, type AuthWert } from './kontext'
import { leseToken, loescheToken, speichereToken } from './token'

/**
 * Verwaltet das Token und reagiert, wenn die API es ablehnt.
 *
 * @param props.children - Die App.
 * @returns Den Kontext-Provider.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()
  const [angemeldet, setAngemeldet] = useState<boolean>(() => leseToken() !== null)

  useEffect(() => {
    /** Wechselt in den abgemeldeten Zustand, wenn die API ein Token ablehnt. */
    const beiAbmeldung = () => {
      setAngemeldet(false)
    }
    window.addEventListener(ABGEMELDET_EREIGNIS, beiAbmeldung)
    return () => {
      window.removeEventListener(ABGEMELDET_EREIGNIS, beiAbmeldung)
    }
  }, [])

  const anmelden = useCallback(async (benutzername: string, passwort: string) => {
    const { token } = await apiAnfrage('/api/auth/login/', tokenSchema, {
      method: 'POST',
      body: { username: benutzername, password: passwort },
    })
    speichereToken(token)
    setAngemeldet(true)
  }, [])

  const abmelden = useCallback(async () => {
    try {
      await apiAnfrage('/api/auth/logout/', leerSchema, { method: 'POST' })
    } catch (error) {
      console.error('Abmelden beim Backend fehlgeschlagen, Token wird lokal gelöscht.', error)
    }
    loescheToken()
    queryClient.clear()
    setAngemeldet(false)
  }, [queryClient])

  const wert = useMemo<AuthWert>(
    () => ({ angemeldet, anmelden, abmelden }),
    [angemeldet, anmelden, abmelden],
  )
  return <AuthKontext.Provider value={wert}>{children}</AuthKontext.Provider>
}
