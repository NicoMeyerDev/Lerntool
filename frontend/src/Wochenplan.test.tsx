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
  aufgaben: [],
}
const PRAXIS = {
  schluessel: 'praxis',
  tageszeit: 'nachmittag',
  titel: 'Praxis und Quiz',
  beschreibung: 'Das Gelernte selbst anwenden.',
  dauer: 'ca. 2–3 Std.',
  aufgaben: [],
}
const TEST_BLOCK = {
  schluessel: 'test',
  tageszeit: 'vormittag',
  titel: 'Test',
  beschreibung: 'Test zum Themenfeld der Woche.',
  dauer: 'ca. 1 Std.',
  aufgaben: [],
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
  lernstart: '2026-11-02',
  nachholen: [],
  nachholen_anzahl: 0,
  auswertung: {
    abschnitte_gelesen: 4,
    quizze_bearbeitet: 2,
    tests_bearbeitet: 1,
    projekte_erledigt: 0,
    trefferquote_prozent: 75,
  },
}

/**
 * Baut eine Aufgabe wie vom Backend geliefert.
 *
 * @param nummer - Nummer des Abschnitts in der Lektion.
 * @param ueberschreiben - Felder, die vom Standard abweichen.
 * @returns Eine Aufgabe für den Plan.
 */
function aufgabe(nummer: number, ueberschreiben: Record<string, unknown> = {}) {
  return {
    abschnitt_id: 100 + nummer,
    lektion_id: 7,
    nummer,
    titel: `Abschnitt ${String(nummer)}`,
    lektion_titel: 'Operatoren',
    thema_titel: 'PHP/Laravel',
    erledigt: false,
    status: 'offen',
    datum: '2026-11-02',
    ...ueberschreiben,
  }
}

/** Ein Plan, dessen Montag vier Abschnitte hat, einer davon erledigt. */
const PLAN_MIT_AUFGABEN = {
  ...PLAN,
  tage: [
    {
      ...PLAN.tage[0],
      bloecke: [
        {
          ...THEORIE,
          aufgaben: [
            aufgabe(1, { erledigt: true, status: 'erledigt' }),
            aufgabe(2),
            aufgabe(3),
            aufgabe(4),
          ],
        },
        PRAXIS,
      ],
    },
    PLAN.tage[1],
  ],
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

  it('zeigt die Abschnitte des Tages als Links in die Lektion', async () => {
    mockeApi({ 'GET /api/wochenplan/': { json: PLAN_MIT_AUFGABEN } })
    renderMitProvidern(<App />, { pfad: '/plan' })

    const montag = (await screen.findByRole('heading', { name: /Montag/ })).closest('li')
    const link = within(montag as HTMLElement).getByRole('link', { name: /Abschnitt 2/ })
    expect(link).toHaveAttribute('href', '/lektionen/7?abschnitt=2')
    expect(within(link).getByText('Heute dran')).toBeInTheDocument()
    expect(within(link).getByText(/PHP\/Laravel · Operatoren/)).toBeInTheDocument()
  })

  it('zeigt den Fortschritt des Tages und markiert Erledigtes', async () => {
    mockeApi({ 'GET /api/wochenplan/': { json: PLAN_MIT_AUFGABEN } })
    renderMitProvidern(<App />, { pfad: '/plan' })

    const montag = (await screen.findByRole('heading', { name: /Montag/ })).closest('li')
    expect(
      within(montag as HTMLElement).getByText('1 von 4 Abschnitten erledigt'),
    ).toBeInTheDocument()
    expect(within(montag as HTMLElement).getByText('✓ erledigt')).toBeInTheDocument()
  })

  it('zeigt keinen Tagesfortschritt an Tagen ohne Abschnitte', async () => {
    mockeApi({ 'GET /api/wochenplan/': { json: PLAN } })
    renderMitProvidern(<App />, { pfad: '/plan' })

    await screen.findByRole('heading', { name: /Montag/ })
    expect(screen.queryByText(/Abschnitten erledigt/)).not.toBeInTheDocument()
  })

  it('zeigt überfällige Abschnitte unter „Nachholen“', async () => {
    const mitNachholen = {
      ...PLAN_MIT_AUFGABEN,
      nachholen_anzahl: 3,
      nachholen: [
        aufgabe(5, { status: 'nachholen', datum: '2026-10-30' }),
        aufgabe(6, { status: 'nachholen', datum: '2026-10-30' }),
      ],
    }
    mockeApi({ 'GET /api/wochenplan/': { json: mitNachholen } })
    renderMitProvidern(<App />, { pfad: '/plan' })

    const bereich = await screen.findByRole('region', { name: 'Nachholen (3)' })
    const link = within(bereich).getByRole('link', { name: /Abschnitt 5/ })
    expect(link).toHaveAttribute('href', '/lektionen/7?abschnitt=5')
    expect(within(link).getByText('Nachholen')).toBeInTheDocument()
    expect(within(link).getByText(/30\.10\.2026/)).toBeInTheDocument()
    expect(within(bereich).getByText('… und 1 weitere.')).toBeInTheDocument()
  })

  it('zeigt keinen Bereich „Nachholen“, wenn nichts offen ist', async () => {
    mockeApi({ 'GET /api/wochenplan/': { json: PLAN_MIT_AUFGABEN } })
    renderMitProvidern(<App />, { pfad: '/plan' })

    await screen.findByRole('heading', { name: /Montag/ })
    expect(screen.queryByRole('region', { name: /Nachholen/ })).not.toBeInTheDocument()
  })

  it('nennt den Lernstart, solange die Woche davor liegt', async () => {
    const vorStart = { ...PLAN, lernstart: '2026-11-16' }
    mockeApi({ 'GET /api/wochenplan/': { json: vorStart } })
    renderMitProvidern(<App />, { pfad: '/plan' })

    expect(await screen.findByText(/Der Plan startet am 16\.11\.2026/)).toBeInTheDocument()
  })

  it('zeigt keinen Starthinweis, wenn der Plan schon läuft', async () => {
    mockeApi({ 'GET /api/wochenplan/': { json: PLAN } })
    renderMitProvidern(<App />, { pfad: '/plan' })

    await screen.findByRole('heading', { name: /Montag/ })
    expect(screen.queryByText(/Der Plan startet am/)).not.toBeInTheDocument()
  })
})
