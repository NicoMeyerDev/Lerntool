/**
 * Tests für die Abschnittsnummer aus der URL.
 */
import { describe, expect, it } from 'vitest'

import { abschnittNummer } from './abschnitt'

describe('abschnittNummer', () => {
  it.each([
    [null, 3, 1],
    ['2', 3, 2],
    ['9', 3, 3],
    ['0', 3, 1],
    ['-1', 3, 1],
    ['abc', 3, 1],
    ['1.5', 3, 1],
    ['2', 0, 1],
  ])('macht aus %j bei %i Abschnitten die Nummer %i', (roh, anzahl, erwartet) => {
    expect(abschnittNummer(roh, anzahl)).toBe(erwartet)
  })
})
