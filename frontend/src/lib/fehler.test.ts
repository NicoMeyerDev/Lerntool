/**
 * Tests für die Fehlermeldungen beim Laden.
 */
import { describe, expect, it } from 'vitest'

import { ApiError } from '../api/client'
import { ladeFehlertext } from './fehler'

describe('ladeFehlertext', () => {
  it('meldet „nicht gefunden“ nur bei 404', () => {
    expect(ladeFehlertext(new ApiError('x', 404), 'Weg.')).toBe('Weg.')
  })

  it.each([new ApiError('x', 500), new ApiError('x', null), new Error('x')])(
    'meldet sonst einen allgemeinen Ladefehler',
    (error) => {
      expect(ladeFehlertext(error, 'Weg.')).toMatch(/^Laden fehlgeschlagen/)
    },
  )
})
