/**
 * Test-Hilfen: App-Teile mit allen Providern rendern und `fetch` gezielt beantworten.
 */
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, type RenderResult } from '@testing-library/react'
import type { ReactElement } from 'react'
import { MemoryRouter } from 'react-router'
import { vi, type Mock } from 'vitest'

import { AuthProvider } from '../auth/AuthProvider'
import { speichereToken } from '../auth/token'

/** Eine vorbereitete Antwort für {@link mockeApi}: Statuscode und JSON-Inhalt. */
export interface Antwort {
  status?: number
  json?: unknown
}

/**
 * Ersetzt `fetch` durch eine Attrappe, die je „METHODE pfad“ eine feste Antwort liefert.
 *
 * Unbekannte Adressen beantwortet sie mit 404, damit Tippfehler im Test auffallen.
 *
 * @param routen - Zuordnung wie `{"GET /api/themen/": {json: [...]}}`.
 * @returns Die Attrappe, um Aufrufe zu prüfen.
 */
export function mockeApi(routen: Record<string, Antwort>): Mock<typeof fetch> {
  const attrappe = vi.fn<typeof fetch>((eingabe, init) => {
    const methode = init?.method ?? 'GET'
    const pfad =
      typeof eingabe === 'string' ? eingabe : eingabe instanceof URL ? eingabe.href : eingabe.url
    const antwort = routen[`${methode} ${pfad}`] ?? {
      status: 404,
      json: { detail: 'Nicht gefunden' },
    }
    const status = antwort.status ?? 200
    if (status === 204) {
      return Promise.resolve(new Response(null, { status }))
    }
    return Promise.resolve(Response.json(antwort.json ?? {}, { status }))
  })
  vi.stubGlobal('fetch', attrappe)
  return attrappe
}

/**
 * Liest den JSON-Inhalt des Aufrufs „METHODE pfad“ aus der Attrappe.
 *
 * @param attrappe - Die Attrappe aus {@link mockeApi}.
 * @param methode - z. B. `POST`.
 * @param pfad - z. B. `/api/quizze/1/abgabe/`.
 * @returns Den gesendeten Inhalt (geparst) oder `undefined`, wenn nicht aufgerufen.
 */
export function gesendeterInhalt(
  attrappe: Mock<typeof fetch>,
  methode: string,
  pfad: string,
): unknown {
  const aufruf = attrappe.mock.calls.find(
    ([eingabe, init]) => eingabe === pfad && (init?.method ?? 'GET') === methode,
  )
  const body = aufruf?.[1]?.body
  return typeof body === 'string' ? JSON.parse(body) : undefined
}

/**
 * Rendert ein Element mit Query-Client, Anmeldung und Router.
 *
 * @param element - Was gerendert wird (z. B. `<App />`).
 * @param optionen.pfad - Start-Adresse im Router, Standard `/`.
 * @param optionen.angemeldet - Ob vorher ein Token gespeichert wird, Standard `true`.
 * @returns Das Ergebnis von `render`.
 */
export function renderMitProvidern(
  element: ReactElement,
  { pfad = '/', angemeldet = true }: { pfad?: string; angemeldet?: boolean } = {},
): RenderResult {
  if (angemeldet) {
    speichereToken('test-token')
  }
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <MemoryRouter initialEntries={[pfad]}>{element}</MemoryRouter>
      </AuthProvider>
    </QueryClientProvider>,
  )
}
