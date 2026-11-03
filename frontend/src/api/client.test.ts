/**
 * Tests für `apiAnfrage`: Token, Schema-Prüfung, Fehler und Abmeldung bei 401.
 */
import { describe, expect, it, vi } from 'vitest'
import { z } from 'zod'

import { leseToken, speichereToken } from '../auth/token'
import { mockeApi } from '../test/hilfen'
import { ABGEMELDET_EREIGNIS, apiAnfrage, ApiError } from './client'

const schema = z.object({ wert: z.number() })

describe('apiAnfrage', () => {
  it('schickt das gespeicherte Token und liefert die geprüfte Antwort', async () => {
    speichereToken('abc')
    const attrappe = mockeApi({ 'GET /api/x/': { json: { wert: 1 } } })

    await expect(apiAnfrage('/api/x/', schema)).resolves.toEqual({ wert: 1 })
    const headers = attrappe.mock.calls[0]?.[1]?.headers as Record<string, string>
    expect(headers.Authorization).toBe('Token abc')
  })

  it('sendet JSON bei POST', async () => {
    const attrappe = mockeApi({ 'POST /api/x/': { json: { wert: 2 } } })

    await apiAnfrage('/api/x/', schema, { method: 'POST', body: { a: 1 } })

    const init = attrappe.mock.calls[0]?.[1]
    expect(init?.body).toBe('{"a":1}')
    expect((init?.headers as Record<string, string>)['Content-Type']).toBe('application/json')
  })

  it('löscht bei 401 das Token und meldet die Abmeldung', async () => {
    speichereToken('abgelaufen')
    mockeApi({ 'GET /api/x/': { status: 401, json: { detail: 'Ungültiges Token.' } } })
    const lauscher = vi.fn()
    window.addEventListener(ABGEMELDET_EREIGNIS, lauscher)

    await expect(apiAnfrage('/api/x/', schema)).rejects.toMatchObject({ status: 401 })

    expect(leseToken()).toBeNull()
    expect(lauscher).toHaveBeenCalledOnce()
    window.removeEventListener(ABGEMELDET_EREIGNIS, lauscher)
  })

  it('übernimmt die Fehlermeldung des Backends', async () => {
    mockeApi({ 'POST /api/x/': { status: 400, json: { detail: 'Das Quiz hat keine Fragen.' } } })

    await expect(apiAnfrage('/api/x/', schema, { method: 'POST' })).rejects.toMatchObject({
      message: 'Das Quiz hat keine Fragen.',
      status: 400,
    })
  })

  it('lehnt Antworten ab, die nicht zum Schema passen', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
    mockeApi({ 'GET /api/x/': { json: { wert: 'kein Zahl' } } })

    await expect(apiAnfrage('/api/x/', schema)).rejects.toBeInstanceOf(ApiError)
  })

  it('kommt mit 204 ohne Inhalt zurecht', async () => {
    mockeApi({ 'POST /api/x/': { status: 204 } })

    await expect(apiAnfrage('/api/x/', z.undefined(), { method: 'POST' })).resolves.toBeUndefined()
  })
})
