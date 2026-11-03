/**
 * Tests für die Token-Ablage im Browser.
 */
import { describe, expect, it, vi } from 'vitest'

import { leseToken, loescheToken, speichereToken } from './token'

describe('Token-Ablage', () => {
  it('speichert, liest und löscht das Token', () => {
    speichereToken('xyz')
    expect(leseToken()).toBe('xyz')

    loescheToken()
    expect(leseToken()).toBeNull()
  })

  it('gilt als abgemeldet, wenn der Speicher gesperrt ist', () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('gesperrt')
    })

    expect(leseToken()).toBeNull()
  })
})
