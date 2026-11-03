/**
 * Tests für die Link-Prüfung.
 */
import { describe, expect, it, vi } from 'vitest'

import { istSichereUrl } from './url'

describe('istSichereUrl', () => {
  it.each(['https://www.php.net/manual/de/', 'http://example.org'])('erlaubt %s', (url) => {
    expect(istSichereUrl(url)).toBe(true)
  })

  it.each(['javascript:alert(1)', 'data:text/html,x', 'ftp://example.org'])(
    'lehnt %s ab',
    (url) => {
      expect(istSichereUrl(url)).toBe(false)
    },
  )

  it('lehnt eine ungültige Adresse ab und protokolliert sie', () => {
    const fehler = vi.spyOn(console, 'error').mockImplementation(() => undefined)

    expect(istSichereUrl('kein link')).toBe(false)
    expect(fehler).toHaveBeenCalled()
  })
})
