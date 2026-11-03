/**
 * Ablauf-Tests für B4: Test mit Zeitlimit und Projektaufgabe mit Checkliste.
 */
import { act, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'

import App from './App'
import { gesendeterInhalt, mockeApi, renderMitProvidern, type Antwort } from './test/hilfen'

/** Test mit zwei Fragen, ohne Lösung (wie vom Backend). */
const TEST = {
  id: 5,
  lektion: 7,
  zeitlimit_minuten: 30,
  fragen: [
    {
      id: 31,
      text: 'Was speichert ein Array?',
      reihenfolge: 1,
      antworten: [
        { id: 41, text: 'Mehrere Werte', reihenfolge: 1 },
        { id: 42, text: 'Nur eine Zahl', reihenfolge: 2 },
      ],
    },
    {
      id: 32,
      text: 'Womit beginnt die Zählung?',
      reihenfolge: 2,
      antworten: [
        { id: 43, text: '0', reihenfolge: 1 },
        { id: 44, text: '1', reihenfolge: 2 },
      ],
    },
  ],
}

/** Antwort auf den Teststart. */
const START = {
  versuch_id: 1,
  gestartet_am: '2026-11-03T10:00:00Z',
  endet_am: '2026-11-03T10:30:00Z',
  sekunden_rest: 1800,
}

/** Auswertung: Frage 1 richtig, Frage 2 falsch. */
const ERGEBNIS = {
  punkte: 1,
  max_punkte: 2,
  bestwert: 1,
  fragen: [
    {
      frage_id: 31,
      gewaehlte_antwort_id: 41,
      richtige_antwort_id: 41,
      ist_richtig: true,
      erklaerung: '',
    },
    {
      frage_id: 32,
      gewaehlte_antwort_id: 44,
      richtige_antwort_id: 43,
      ist_richtig: false,
      erklaerung: 'Numerische Schlüssel beginnen bei 0.',
    },
  ],
}

/** Standard-Antworten für die Testseite. */
const testRouten = (): Record<string, Antwort> => ({
  'GET /api/tests/5/': { json: TEST },
  'POST /api/tests/5/start/': { json: START },
  'POST /api/tests/5/abgabe/': { json: ERGEBNIS },
  'GET /api/fortschritt/': { json: [] },
})

afterEach(() => {
  vi.useRealTimers()
})

describe('Test mit Zeitlimit', () => {
  it('zeigt vor dem Start nur den Hinweis, noch keine Fragen', async () => {
    const attrappe = mockeApi(testRouten())
    renderMitProvidern(<App />, { pfad: '/tests/5' })

    expect(await screen.findByText(/dauert höchstens/)).toHaveTextContent('30 Minuten')
    expect(screen.getByRole('link', { name: '← Zur Lektion' })).toHaveAttribute(
      'href',
      '/lektionen/7',
    )
    expect(screen.queryByText(/Was speichert ein Array\?/)).not.toBeInTheDocument()
    expect(attrappe).not.toHaveBeenCalledWith(
      '/api/tests/5/start/',
      expect.objectContaining({ method: 'POST' }),
    )
  })

  it('startet den Test, zeigt Fragen und die Uhr mit der Restzeit des Servers', async () => {
    const attrappe = mockeApi(testRouten())
    renderMitProvidern(<App />, { pfad: '/tests/5' })

    await userEvent.click(await screen.findByRole('button', { name: 'Test starten' }))

    expect(await screen.findByText(/Was speichert ein Array\?/)).toBeInTheDocument()
    expect(screen.getByRole('timer', { name: 'Verbleibende Zeit' })).toHaveTextContent('30:00')
    expect(attrappe).toHaveBeenCalledWith(
      '/api/tests/5/start/',
      expect.objectContaining({ method: 'POST' }),
    )
  })

  it('gibt ab, auch mit unbeantworteten Fragen, und zeigt die Auswertung', async () => {
    const attrappe = mockeApi(testRouten())
    renderMitProvidern(<App />, { pfad: '/tests/5' })
    await userEvent.click(await screen.findByRole('button', { name: 'Test starten' }))

    await userEvent.click(await screen.findByLabelText('Mehrere Werte'))
    expect(screen.getByText(/1 von 2 Fragen beantwortet/)).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Test abgeben' }))

    expect(await screen.findByText('1 von 2 richtig')).toBeInTheDocument()
    expect(screen.getByText('Numerische Schlüssel beginnen bei 0.')).toBeInTheDocument()
    expect(screen.queryByRole('timer')).not.toBeInTheDocument()
    expect(gesendeterInhalt(attrappe, 'POST', '/api/tests/5/abgabe/')).toEqual({
      antworten: [{ frage: 31, antwort: 41 }],
    })
  })

  it('führt mit „Nochmal versuchen“ zurück zum Start', async () => {
    mockeApi(testRouten())
    renderMitProvidern(<App />, { pfad: '/tests/5' })
    await userEvent.click(await screen.findByRole('button', { name: 'Test starten' }))
    await userEvent.click(await screen.findByRole('button', { name: 'Test abgeben' }))

    await userEvent.click(await screen.findByRole('button', { name: 'Nochmal versuchen' }))

    expect(screen.getByRole('button', { name: 'Test starten' })).toBeInTheDocument()
    expect(screen.queryByText('1 von 2 richtig')).not.toBeInTheDocument()
  })

  it('zählt herunter und gibt bei Ablauf automatisch mit den gewählten Antworten ab', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true })
    const attrappe = mockeApi({
      ...testRouten(),
      'POST /api/tests/5/start/': { json: { ...START, sekunden_rest: 3 } },
    })
    const nutzer = userEvent.setup({ advanceTimers: vi.advanceTimersByTime.bind(vi) })
    renderMitProvidern(<App />, { pfad: '/tests/5' })
    await nutzer.click(await screen.findByRole('button', { name: 'Test starten' }))
    await nutzer.click(await screen.findByLabelText('Mehrere Werte'))

    expect(screen.getByRole('timer')).toHaveTextContent('00:0')
    await act(async () => {
      await vi.advanceTimersByTimeAsync(4000)
    })

    expect(await screen.findByText('1 von 2 richtig')).toBeInTheDocument()
    expect(gesendeterInhalt(attrappe, 'POST', '/api/tests/5/abgabe/')).toEqual({
      antworten: [{ frage: 31, antwort: 41 }],
    })
    const abgaben = attrappe.mock.calls.filter(([adresse]) => adresse === '/api/tests/5/abgabe/')
    expect(abgaben).toHaveLength(1)
  })

  it('meldet eine abgelehnte Abgabe und bietet einen neuen Versuch an', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
    mockeApi({
      ...testRouten(),
      'POST /api/tests/5/abgabe/': {
        status: 409,
        json: { detail: 'Das Zeitlimit ist abgelaufen.' },
      },
    })
    renderMitProvidern(<App />, { pfad: '/tests/5' })
    await userEvent.click(await screen.findByRole('button', { name: 'Test starten' }))
    await userEvent.click(await screen.findByRole('button', { name: 'Test abgeben' }))

    expect(
      await screen.findByText(/Abgabe fehlgeschlagen: Das Zeitlimit ist abgelaufen\./),
    ).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Neuen Versuch starten' }))

    expect(screen.getByRole('button', { name: 'Test starten' })).toBeInTheDocument()
  })

  it('meldet einen Fehler beim Start', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
    mockeApi({ ...testRouten(), 'POST /api/tests/5/start/': { status: 500, json: {} } })
    renderMitProvidern(<App />, { pfad: '/tests/5' })

    await userEvent.click(await screen.findByRole('button', { name: 'Test starten' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Start fehlgeschlagen')
  })

  it('meldet einen Test ohne Fragen', async () => {
    mockeApi({ ...testRouten(), 'GET /api/tests/5/': { json: { ...TEST, fragen: [] } } })
    renderMitProvidern(<App />, { pfad: '/tests/5' })

    expect(await screen.findByText('Dieser Test hat noch keine Fragen.')).toBeInTheDocument()
  })

  it('meldet einen unbekannten Test und eine ungültige Adresse', async () => {
    mockeApi({})
    const { unmount } = renderMitProvidern(<App />, { pfad: '/tests/99' })
    expect(await screen.findByRole('alert')).toHaveTextContent('nicht gefunden')
    unmount()

    const attrappe = mockeApi({})
    renderMitProvidern(<App />, { pfad: '/tests/abc' })
    expect(screen.getByRole('alert')).toHaveTextContent('Ungültiger Test.')
    expect(attrappe).not.toHaveBeenCalledWith(
      expect.stringContaining('/api/tests/'),
      expect.anything(),
    )
  })

  it('verlinkt den Test auf der Lektionsseite', async () => {
    mockeApi({
      'GET /api/lektionen/7/': {
        json: {
          id: 7,
          phase: 1,
          titel: 'Arrays',
          slug: 'arrays',
          zusammenfassung: '',
          reihenfolge: 1,
          abschnitte: [{ id: 11, titel: 'Start', inhalt: 'Text', reihenfolge: 1, quiz_id: null }],
          quellen: [],
          test_id: 5,
        },
      },
      'GET /api/fortschritt/': { json: [] },
    })
    renderMitProvidern(<App />, { pfad: '/lektionen/7' })

    expect(await screen.findByRole('link', { name: /Test zu dieser Lektion/ })).toHaveAttribute(
      'href',
      '/tests/5',
    )
  })
})

/** Projektaufgabe mit drei Punkten, einer davon erledigt. */
const PROJEKT = {
  id: 3,
  phase: 2,
  titel: 'Einkaufsliste',
  beschreibung: 'Baue eine **Einkaufsliste**.',
  punkte: [
    { id: 61, text: 'Array anlegen', reihenfolge: 1, erledigt: true },
    { id: 62, text: 'Eintrag hinzufügen', reihenfolge: 2, erledigt: false },
    { id: 63, text: 'Liste ausgeben', reihenfolge: 3, erledigt: false },
  ],
  erledigt: 1,
  gesamt: 3,
  abgeschlossen: false,
}

describe('Projektaufgabe', () => {
  it('zeigt Aufgabe, Checkliste, Fortschritt und Auswertung', async () => {
    mockeApi({ 'GET /api/projekte/3/': { json: PROJEKT } })
    renderMitProvidern(<App />, { pfad: '/projekte/3' })

    expect(
      await screen.findByRole('heading', { name: 'Projekt: Einkaufsliste' }),
    ).toBeInTheDocument()
    expect(screen.getByText('Einkaufsliste', { selector: 'strong' })).toBeInTheDocument()
    expect(screen.getByLabelText('Array anlegen')).toBeChecked()
    expect(screen.getByLabelText('Eintrag hinzufügen')).not.toBeChecked()
    expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '1')
    expect(screen.getByText('Schon 1 von 3 erledigt – noch 2 offen.')).toBeInTheDocument()
  })

  it('hakt einen Punkt ab und zeigt den neuen Stand des Backends', async () => {
    const attrappe = mockeApi({
      'GET /api/projekte/3/': { json: PROJEKT },
      'PUT /api/projekte/3/punkte/62/': {
        json: {
          ...PROJEKT,
          punkte: PROJEKT.punkte.map((p) => (p.id === 62 ? { ...p, erledigt: true } : p)),
          erledigt: 2,
        },
      },
      'GET /api/fortschritt/': { json: [] },
    })
    renderMitProvidern(<App />, { pfad: '/projekte/3' })

    await userEvent.click(await screen.findByLabelText('Eintrag hinzufügen'))

    expect(await screen.findByText('Schon 2 von 3 erledigt – noch 1 offen.')).toBeInTheDocument()
    expect(screen.getByLabelText('Eintrag hinzufügen')).toBeChecked()
    expect(gesendeterInhalt(attrappe, 'PUT', '/api/projekte/3/punkte/62/')).toEqual({
      erledigt: true,
    })
  })

  it('nimmt einen Haken zurück', async () => {
    const attrappe = mockeApi({
      'GET /api/projekte/3/': { json: PROJEKT },
      'PUT /api/projekte/3/punkte/61/': {
        json: {
          ...PROJEKT,
          punkte: PROJEKT.punkte.map((p) => (p.id === 61 ? { ...p, erledigt: false } : p)),
          erledigt: 0,
        },
      },
      'GET /api/fortschritt/': { json: [] },
    })
    renderMitProvidern(<App />, { pfad: '/projekte/3' })

    await userEvent.click(await screen.findByLabelText('Array anlegen'))

    expect(
      await screen.findByText('Noch nichts abgehakt. Fang mit dem ersten Punkt an.'),
    ).toBeInTheDocument()
    expect(gesendeterInhalt(attrappe, 'PUT', '/api/projekte/3/punkte/61/')).toEqual({
      erledigt: false,
    })
  })

  it('zeigt bei vollständiger Checkliste den Abschluss', async () => {
    mockeApi({
      'GET /api/projekte/3/': {
        json: {
          ...PROJEKT,
          punkte: PROJEKT.punkte.map((p) => ({ ...p, erledigt: true })),
          erledigt: 3,
          abgeschlossen: true,
        },
      },
    })
    renderMitProvidern(<App />, { pfad: '/projekte/3' })

    expect(await screen.findByText('Projekt abgeschlossen!')).toBeInTheDocument()
    expect(screen.getByRole('status')).toHaveTextContent('Alle 3 Punkte sind erledigt.')
  })

  it('meldet, wenn das Abhaken nicht gespeichert werden konnte', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
    mockeApi({
      'GET /api/projekte/3/': { json: PROJEKT },
      'PUT /api/projekte/3/punkte/62/': { status: 500, json: {} },
    })
    renderMitProvidern(<App />, { pfad: '/projekte/3' })

    await userEvent.click(await screen.findByLabelText('Eintrag hinzufügen'))

    expect(await screen.findByRole('alert')).toHaveTextContent('Speichern fehlgeschlagen')
    expect(screen.getByLabelText('Eintrag hinzufügen')).not.toBeChecked()
  })

  it('meldet eine Aufgabe ohne Checkliste', async () => {
    mockeApi({
      'GET /api/projekte/3/': { json: { ...PROJEKT, punkte: [], erledigt: 0, gesamt: 0 } },
    })
    renderMitProvidern(<App />, { pfad: '/projekte/3' })

    expect(await screen.findByText('Diese Aufgabe hat noch keine Checkliste.')).toBeInTheDocument()
  })

  it('meldet ein unbekanntes Projekt und eine ungültige Adresse', async () => {
    mockeApi({})
    const { unmount } = renderMitProvidern(<App />, { pfad: '/projekte/99' })
    expect(await screen.findByRole('alert')).toHaveTextContent('nicht gefunden')
    unmount()

    renderMitProvidern(<App />, { pfad: '/projekte/abc' })
    expect(screen.getByRole('alert')).toHaveTextContent('Ungültiges Projekt.')
  })

  it('verlinkt Projekte auf der Themenseite', async () => {
    mockeApi({
      'GET /api/themen/php-laravel/': {
        json: {
          id: 1,
          titel: 'PHP/Laravel',
          slug: 'php-laravel',
          beschreibung: '',
          reihenfolge: 1,
          phasen: [
            {
              id: 2,
              titel: 'PHP-Basics',
              slug: 'php-basics',
              beschreibung: '',
              reihenfolge: 1,
              lektionen: [],
              projektaufgaben: [{ id: 3, titel: 'Einkaufsliste', reihenfolge: 1 }],
            },
          ],
        },
      },
    })
    renderMitProvidern(<App />, { pfad: '/themen/php-laravel' })

    expect(await screen.findByRole('link', { name: 'Projekt: Einkaufsliste' })).toHaveAttribute(
      'href',
      '/projekte/3',
    )
  })
})
