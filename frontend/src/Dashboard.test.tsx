/**
 * Tests für B5: Dashboard auf der Startseite.
 */
import { screen, within } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import App from './App'
import { mockeApi, renderMitProvidern, type Antwort } from './test/hilfen'

/** Dashboard eines Nutzers mit etwas Fortschritt. */
const DASHBOARD = {
  xp: 130,
  level: 2,
  xp_im_level: 30,
  xp_pro_level: 100,
  statistik: {
    abschnitte_gelesen: 3,
    abschnitte_gesamt: 12,
    quizze_bearbeitet: 2,
    quizze_gesamt: 12,
    tests_bearbeitet: 0,
    tests_gesamt: 4,
    projekte_erledigt: 0,
    projekte_gesamt: 1,
    trefferquote_prozent: 75,
  },
  themen: [{ slug: 'php-laravel', titel: 'PHP/Laravel', erledigt: 5, gesamt: 29 }],
  abzeichen: [
    {
      schluessel: 'erster-schritt',
      titel: 'Erster Schritt',
      beschreibung: 'Einen Abschnitt gelesen',
      erreicht: true,
    },
    {
      schluessel: 'testlauf',
      titel: 'Testlauf',
      beschreibung: 'Den ersten Test abgegeben',
      erreicht: false,
    },
  ],
  meilensteine: [
    {
      schluessel: 'abschnitte',
      titel: 'Abschnitte gelesen',
      aktuell: 3,
      ziel: 10,
      erreicht: false,
    },
    { schluessel: 'xp', titel: 'Erfahrungspunkte', aktuell: 1000, ziel: 1000, erreicht: true },
  ],
}

/** Antworten der Startseite. */
const startRouten = (dashboard: Antwort): Record<string, Antwort> => ({
  'GET /api/health/': { json: { status: 'ok', datenbank: 'ok' } },
  'GET /api/themen/': { json: [] },
  'GET /api/dashboard/': dashboard,
})

describe('Dashboard', () => {
  it('zeigt Level, XP-Balken, Kennzahlen und Trefferquote', async () => {
    mockeApi(startRouten({ json: DASHBOARD }))
    renderMitProvidern(<App />)

    const bereich = await screen.findByRole('region', { name: 'Dein Fortschritt' })
    expect(await within(bereich).findByText('Insgesamt 130 XP')).toBeInTheDocument()
    expect(
      within(bereich).getByRole('progressbar', { name: '30 von 100 XP bis Level 3' }),
    ).toHaveAttribute('aria-valuenow', '30')
    expect(within(bereich).getByText('3/12')).toBeInTheDocument()
    expect(within(bereich).getByText('Abschnitte gelesen', { selector: 'p' })).toBeInTheDocument()
    expect(within(bereich).getByText('75 %')).toBeInTheDocument()
  })

  it('zeigt den Fortschritt je Thema', async () => {
    mockeApi(startRouten({ json: DASHBOARD }))
    renderMitProvidern(<App />)

    expect(
      await screen.findByRole('progressbar', { name: 'PHP/Laravel: 5 von 29' }),
    ).toHaveAttribute('aria-valuenow', '5')
  })

  it('zeigt erreichte und noch nicht erreichte Abzeichen', async () => {
    mockeApi(startRouten({ json: DASHBOARD }))
    renderMitProvidern(<App />)

    const erreicht = (await screen.findByText('Erster Schritt')).closest('li')
    const offen = screen.getByText('Testlauf').closest('li')
    expect(erreicht).toHaveTextContent('Erreicht')
    expect(offen).toHaveTextContent('Noch nicht erreicht')
  })

  it('zeigt Meilensteine mit Ziel und markiert erreichte', async () => {
    mockeApi(startRouten({ json: DASHBOARD }))
    renderMitProvidern(<App />)

    expect(
      await screen.findByRole('progressbar', { name: 'Abschnitte gelesen: 3 von 10' }),
    ).toHaveAttribute('aria-valuemax', '10')
    expect(
      screen.getByRole('progressbar', { name: 'Erfahrungspunkte: 1000 von 1000 ✓' }),
    ).toBeInTheDocument()
  })

  it('sagt „noch kein Ergebnis“ ohne Trefferquote', async () => {
    const leer = {
      ...DASHBOARD,
      statistik: { ...DASHBOARD.statistik, trefferquote_prozent: null },
    }
    mockeApi(startRouten({ json: leer }))
    renderMitProvidern(<App />)

    expect(await screen.findByText('noch kein Ergebnis')).toBeInTheDocument()
  })

  it('meldet, wenn das Dashboard nicht geladen werden konnte', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
    mockeApi(startRouten({ status: 500, json: {} }))
    renderMitProvidern(<App />)

    expect(
      await screen.findByText('Der Fortschritt konnte nicht geladen werden.'),
    ).toBeInTheDocument()
  })
})
