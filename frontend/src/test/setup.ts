/**
 * Gemeinsame Test-Einrichtung: DOM-Matcher und Aufräumen (DOM, Mocks, Token) nach jedem Test.
 */
import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

afterEach(() => {
  cleanup()
  localStorage.clear()
  vi.restoreAllMocks()
  vi.unstubAllGlobals()
})

// jsdom kennt kein Scrollen; die Lektionsseite scrollt beim Blättern nach oben.
window.scrollTo = () => undefined
