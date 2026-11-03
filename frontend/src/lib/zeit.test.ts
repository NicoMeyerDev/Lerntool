import { describe, expect, it } from 'vitest'

import { formatiereRestzeit } from './zeit'

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
