/**
 * Tests für den Health-Check-Zugriff.
 */
import { describe, expect, it, vi } from 'vitest'

import { ApiError } from './client'
import { fetchHealth, isHealthResponse } from './health'

/**
 * Ersetzt `fetch` durch eine Attrappe, die eine JSON-Antwort liefert.
 *
 * @param status - HTTP-Statuscode der Antwort.
 * @param body - JSON-Inhalt der Antwort.
 * @returns Die Attrappe, um Aufrufe zu prüfen.
 */
function mockFetch(status: number, body: unknown) {
  const fetchMock = vi.fn(() => Promise.resolve(Response.json(body, { status })))
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

describe('isHealthResponse', () => {
  it('erkennt eine gültige Antwort', () => {
    expect(isHealthResponse({ status: 'ok', datenbank: 'ok' })).toBe(true)
  })

  it.each([null, 'ok', {}, { status: 'unbekannt', datenbank: 'ok' }, { status: 'ok' }])(
    'lehnt ungültige Werte ab: %j',
    (wert) => {
      expect(isHealthResponse(wert)).toBe(false)
    },
  )
})

describe('fetchHealth', () => {
  it('liefert die Antwort bei 200 und ruft den richtigen Pfad auf', async () => {
    const fetchMock = mockFetch(200, { status: 'ok', datenbank: 'ok' })

    await expect(fetchHealth()).resolves.toEqual({ status: 'ok', datenbank: 'ok' })
    expect(fetchMock).toHaveBeenCalledWith('/api/health/', expect.anything())
  })

  it('liefert die Fehler-Antwort bei 503', async () => {
    mockFetch(503, { status: 'fehler', datenbank: 'nicht erreichbar' })

    await expect(fetchHealth()).resolves.toEqual({
      status: 'fehler',
      datenbank: 'nicht erreichbar',
    })
  })

  it('wirft ApiError bei unerwartetem Statuscode', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
    mockFetch(500, { detail: 'Serverfehler' })

    await expect(fetchHealth()).rejects.toBeInstanceOf(ApiError)
  })

  it('wirft ApiError, wenn die Antwort kein JSON ist', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.resolve(new Response('<html></html>', { status: 200 }))),
    )

    await expect(fetchHealth()).rejects.toMatchObject({
      message: 'Ungültige Antwort der API',
      status: 200,
    })
  })

  it('wirft ApiError, wenn das Backend nicht antwortet', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.reject(new TypeError('Failed to fetch'))),
    )

    await expect(fetchHealth()).rejects.toMatchObject({ name: 'ApiError', status: null })
  })
})
