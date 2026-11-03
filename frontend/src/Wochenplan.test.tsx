/**
 * Tests für B6: Wochen- und Tagesplan.
 */
import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import App from './App'
import { mockeApi, renderMitProvidern } from './test/hilfen'

/** Block-Vorlagen wie vom Backend geliefert. */
const THEORIE = {
  schluessel: 'theorie',
  tageszeit: 'vormittag',
  titel: 'Theorie',
  beschreibung: 'Lektion lesen, danach das Quiz zum Abschnitt.',
  dauer: 'ca. 3 Std.',
}
const PRAXIS = {
  schluessel: 'praxis',
  tageszeit: 'nachmittag',
  titel: 'Praxis und Quiz',
  beschreibung: 'Das Gelernte selbst anwenden.',
  dauer: 'ca. 2–3 Std.',
}
const TEST_BLOCK = {
  schluessel: 'test',
  tageszeit: 'vormittag',
  titel: 'Test',
  beschreibung: 'Test zum Themenfeld der Woche.',
  dauer: 'ca. 1 Std.',
}

/** Eine Woche (2.–8. November 2026) mit zwei Tagen zur Kürze. */
const PLAN = {
  woche_start: '2026-11-02',
  woche_ende: '2026-11-08',
  vorherige_woche: '2026-10-26',
  naechste_woche: '2026-11-09',
  ist_aktuelle_woche: true,
  tage: [
    {
      datum: '2026-11-02',
      wochentag: 'Montag',
      ist_heute: true,
      bloecke: [THEORIE, PRAXIS],
    },
    {
      datum: '2026-11-06',
      wochentag: 'Freitag',
      ist_heute: false,
      bloecke: [TEST_BLOCK],
    },
  ],
  auswertung: {
    abschnitte_gelesen: 4,
    quizze_bearbeitet: 2,
    tests_bearbeitet: 1,
    projekte_erledigt: 0,
    trefferquote_prozent: 75,
  },
}

describe('Wochenplan', () => {
  it('zeigt Tage mit festen Blöcken und markiert heute', async () => {
    mockeApi({ 'GET /api/wochenplan/': { json: PLAN } })
    renderMitProvidern(<App />, { pfad: '/plan' })

    const montag = (await screen.findByRole('heading', { name: /Montag, 02\.11\.2026/ })).closest(
      'li',
    )
    expect(montag).not.toBeNull()
    expect(montag).toHaveAttribute('aria-current', 'date')
    expect(within(montag as HTMLElement).getByText(/Vormittag, ca\. 3 Std\./)).toBeInTheDocument()
    expect(
      within(montag as HTMLElement).getByText(/Nachmittag, ca\. 2–3 Std\./),
    ).toBeInTheDocument()
    const freitag = screen.getByRole('heading', { name: /Freitag/ }).closest('li')
    expect(freitag).not.toHaveAttribute('aria-current')
    expect(screen.queryByRole('link', { name: 'Zur aktuellen Woche' })).not.toBeInTheDocument()
  })

  it('zeigt die Wochenauswertung', async () => {
    mockeApi({ 'GET /api/wochenplan/': { json: PLAN } })
    renderMitProvidern(<App />, { pfad: '/plan' })

    const bereich = await screen.findByRole('region', { name: 'Wochenauswertung' })
    expect(within(bereich).getByText('4')).toBeInTheDocument()
    expect(within(bereich).getByText('Abschnitte gelesen')).toBeInTheDocument()
    expect(within(bereich).getByText('75 %')).toBeInTheDocument()
  })

  it('sagt „noch kein Ergebnis“ ohne Trefferquote', async () => {
    const leer = { ...PLAN, auswertung: { ...PLAN.auswertung, trefferquote_prozent: null } }
    mockeApi({ 'GET /api/wochenplan/': { json: leer } })
    renderMitProvidern(<App />, { pfad: '/plan' })

    expect(await screen.findByText('noch kein Ergebnis')).toBeInTheDocument()
  })

  it('blättert zur Folgewoche und bietet den Rückweg zur aktuellen an', async () => {
    const naechste = {
      ...PLAN,
      woche_start: '2026-11-09',
      woche_ende: '2026-11-15',
      ist_aktuelle_woche: false,
      tage: [{ ...PLAN.tage[0], datum: '2026-11-09', ist_heute: false }],
    }
    const attrappe = mockeApi({
      'GET /api/wochenplan/': { json: PLAN },
      'GET /api/wochenplan/?datum=2026-11-09': { json: naechste },
    })
    renderMitProvidern(<App />, { pfad: '/plan' })

    await userEvent.click(await screen.findByRole('link', { name: /Folgewoche/ }))

    expect(await screen.findByRole('heading', { name: /09\.11\.2026/ })).toBeInTheDocument()
    expect(attrappe).toHaveBeenCalledWith('/api/wochenplan/?datum=2026-11-09', expect.anything())
    expect(screen.getByRole('link', { name: 'Zur aktuellen Woche' })).toBeInTheDocument()
  })

  it('ist über „Plan“ in der Kopfzeile erreichbar', async () => {
    mockeApi({
      'GET /api/health/': { json: { status: 'ok', datenbank: 'ok' } },
      'GET /api/themen/': { json: [] },
      'GET /api/dashboard/': { status: 500, json: {} },
      'GET /api/wochenplan/': { json: PLAN },
    })
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
    renderMitProvidern(<App />)

    await userEvent.click(await screen.findByRole('link', { name: 'Plan' }))

    expect(await screen.findByRole('heading', { name: 'Wochenplan' })).toBeInTheDocument()
  })

  it('meldet, wenn der Plan nicht geladen werden konnte', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
    mockeApi({ 'GET /api/wochenplan/': { status: 500, json: {} } })
    renderMitProvidern(<App />, { pfad: '/plan' })

    expect(await screen.findByText('Der Plan konnte nicht geladen werden.')).toBeInTheDocument()
  })
})
