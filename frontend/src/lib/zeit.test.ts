import { describe, expect, it } from 'vitest'

import { formatiereDatum, formatiereRestzeit } from './zeit'

describe('formatiereRestzeit', () => {
  it.each([
    [1800, '30:00'],
    [65, '01:05'],
    [9, '00:09'],
    [0, '00:00'],
    [-5, '00:00'],
    [59.9, '00:59'],
  ])('formatiert %f Sekunden als %s', (sekunden, erwartet) => {
    expect(formatiereRestzeit(sekunden)).toBe(erwartet)
  })
})

describe('formatiereDatum', () => {
  it.each([
    ['2026-11-04', '04.11.2026'],
    ['2027-01-31', '31.01.2027'],
    ['kein Datum', 'kein Datum'],
  ])('formatiert %s als %s', (iso, erwartet) => {
    expect(formatiereDatum(iso)).toBe(erwartet)
  })
})
