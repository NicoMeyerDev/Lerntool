/**
 * Ablauf-Tests über die ganze App: Anmeldung, Navigation, Lektion lesen, Quiz abgeben.
 */
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import App from './App'
import { leseToken } from './auth/token'
import { gesendeterInhalt, mockeApi, renderMitProvidern, type Antwort } from './test/hilfen'

/** Health-Check, den die Startseite immer aufruft. */
const HEALTH: Record<string, Antwort> = {
  'GET /api/health/': { json: { status: 'ok', datenbank: 'ok' } },
}

/** Eine Lektion mit zwei Abschnitten; nur der erste hat ein Quiz. */
const LEKTION = {
  id: 7,
  phase: 1,
  titel: 'Arrays',
  slug: 'arrays',
  zusammenfassung: '',
  reihenfolge: 1,
  abschnitte: [
    {
      id: 11,
      titel: 'Was ist ein Array?',
      inhalt: 'Ein **Array** ist eine Liste.',
      reihenfolge: 1,
      quiz_id: 21,
    },
    {
      id: 12,
      titel: 'Schlüssel',
      inhalt: 'Arrays haben Schlüssel.',
      reihenfolge: 2,
      quiz_id: null,
    },
  ],
  quellen: [
    {
      titel: 'PHP-Handbuch: Arrays',
      url: 'https://www.php.net/manual/de/language.types.array.php',
    },
  ],
  test_id: null,
}

/** Quiz mit zwei Fragen, ohne Lösung (wie vom Backend). */
const QUIZ = {
  id: 21,
  abschnitt: 11,
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

describe('Anmeldung', () => {
  it('leitet ohne Anmeldung zum Login um', () => {
    mockeApi(HEALTH)
    renderMitProvidern(<App />, { angemeldet: false })

    expect(screen.getByRole('button', { name: 'Anmelden' })).toBeInTheDocument()
  })

  it('meldet an, speichert das Token und zeigt die Themen', async () => {
    const attrappe = mockeApi({
      ...HEALTH,
      'POST /api/auth/login/': { json: { token: 'neu' } },
      'GET /api/themen/': {
        json: [
          { id: 1, titel: 'PHP/Laravel', slug: 'php-laravel', beschreibung: '', reihenfolge: 1 },
        ],
      },
    })
    renderMitProvidern(<App />, { pfad: '/login', angemeldet: false })

    await userEvent.type(screen.getByLabelText('Benutzername'), 'lernender')
    await userEvent.type(screen.getByLabelText('Passwort'), 'geheim')
    await userEvent.click(screen.getByRole('button', { name: 'Anmelden' }))

    expect(await screen.findByRole('link', { name: 'PHP/Laravel' })).toBeInTheDocument()
    expect(leseToken()).toBe('neu')
    expect(gesendeterInhalt(attrappe, 'POST', '/api/auth/login/')).toEqual({
      username: 'lernender',
      password: 'geheim',
    })
  })

  it.each([
    [400, 'Benutzername oder Passwort ist falsch.'],
    [429, 'Zu viele Versuche. Bitte warte eine Minute.'],
  ])('zeigt bei Status %i eine verständliche Meldung', async (status, meldung) => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
    mockeApi({ 'POST /api/auth/login/': { status, json: {} } })
    renderMitProvidern(<App />, { pfad: '/login', angemeldet: false })

    await userEvent.type(screen.getByLabelText('Benutzername'), 'x')
    await userEvent.type(screen.getByLabelText('Passwort'), 'y')
    await userEvent.click(screen.getByRole('button', { name: 'Anmelden' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(meldung)
    expect(leseToken()).toBeNull()
  })

  it('meldet ab und kehrt zum Login zurück', async () => {
    const attrappe = mockeApi({
      ...HEALTH,
      'GET /api/themen/': { json: [] },
      'POST /api/auth/logout/': { status: 204 },
    })
    renderMitProvidern(<App />)

    await userEvent.click(await screen.findByRole('button', { name: 'Abmelden' }))

    expect(await screen.findByRole('button', { name: 'Anmelden' })).toBeInTheDocument()
    expect(leseToken()).toBeNull()
    expect(attrappe).toHaveBeenCalledWith(
      '/api/auth/logout/',
      expect.objectContaining({ method: 'POST' }),
    )
  })

  it('wechselt zum Login, wenn das Backend das Token ablehnt', async () => {
    mockeApi({
      ...HEALTH,
      'GET /api/themen/': { status: 401, json: { detail: 'Ungültiges Token.' } },
    })
    renderMitProvidern(<App />)

    expect(await screen.findByRole('button', { name: 'Anmelden' })).toBeInTheDocument()
  })
})

describe('Themenseite', () => {
  it('zeigt Phasen mit Links zu den Lektionen', async () => {
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
              lektionen: [
                { id: 7, titel: 'Arrays', slug: 'arrays', zusammenfassung: '', reihenfolge: 1 },
              ],
              projektaufgaben: [{ id: 3, titel: 'Einkaufsliste', reihenfolge: 1 }],
            },
          ],
        },
      },
    })
    renderMitProvidern(<App />, { pfad: '/themen/php-laravel' })

    expect(await screen.findByRole('heading', { name: 'Phase 1: PHP-Basics' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Arrays' })).toHaveAttribute('href', '/lektionen/7')
    expect(screen.getByRole('link', { name: 'Projekt: Einkaufsliste' })).toHaveAttribute(
      'href',
      '/projekte/3',
    )
  })

  it('meldet ein unbekanntes Thema', async () => {
    mockeApi({})
    renderMitProvidern(<App />, { pfad: '/themen/gibt-es-nicht' })

    expect(await screen.findByRole('alert')).toHaveTextContent('nicht gefunden')
  })

  it('meldet einen Serverfehler nicht als „nicht gefunden“', async () => {
    mockeApi({ 'GET /api/themen/php-laravel/': { status: 500, json: {} } })
    renderMitProvidern(<App />, { pfad: '/themen/php-laravel' })

    expect(await screen.findByRole('alert')).toHaveTextContent('Laden fehlgeschlagen')
  })
})

describe('Lektion und Quiz', () => {
  /** Standard-Antworten für die Lektionsseite. */
  const lektionsRouten = (fortschritt: unknown[] = []): Record<string, Antwort> => ({
    'GET /api/lektionen/7/': { json: LEKTION },
    'GET /api/quizze/21/': { json: QUIZ },
    'GET /api/fortschritt/': { json: fortschritt },
    'POST /api/abschnitte/11/gelesen/': {
      json: {
        id: 1,
        abschnitt: 11,
        quiz: null,
        test: null,
        projektaufgabe: null,
        punkte: null,
        max_punkte: null,
        erledigt_am: '2026-11-03T10:00:00Z',
      },
    },
    'POST /api/quizze/21/abgabe/': { json: ERGEBNIS },
  })

  it('zeigt den ersten Abschnitt mit formatiertem Text, Quiz und Quellen', async () => {
    mockeApi(lektionsRouten())
    renderMitProvidern(<App />, { pfad: '/lektionen/7' })

    expect(await screen.findByRole('heading', { name: 'Was ist ein Array?' })).toBeInTheDocument()
    expect(screen.getByText('Abschnitt 1 von 2')).toBeInTheDocument()
    expect(screen.getByText('Array').tagName).toBe('STRONG')
    expect(await screen.findByText(/Was speichert ein Array\?/)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'PHP-Handbuch: Arrays' })).toHaveAttribute(
      'href',
      'https://www.php.net/manual/de/language.types.array.php',
    )
  })

  it('gibt erst ab, wenn alle Fragen beantwortet sind, und zeigt die Auswertung', async () => {
    const attrappe = mockeApi(lektionsRouten())
    renderMitProvidern(<App />, { pfad: '/lektionen/7' })
    const abgeben = await screen.findByRole('button', { name: 'Antworten abgeben' })

    expect(abgeben).toBeDisabled()
    await userEvent.click(screen.getByLabelText('Mehrere Werte'))
    expect(abgeben).toBeDisabled()
    await userEvent.click(screen.getByLabelText('1'))
    expect(abgeben).toBeEnabled()
    await userEvent.click(abgeben)

    expect(await screen.findByText('1 von 2 richtig')).toBeInTheDocument()
    expect(screen.getByText(/Bestwert: 1 von 2/)).toBeInTheDocument()
    expect(screen.getByText('Numerische Schlüssel beginnen bei 0.')).toBeInTheDocument()
    expect(screen.getByText('✗ deine Antwort')).toBeInTheDocument()
    expect(screen.getAllByText('✓ richtig')).toHaveLength(2)
    expect(gesendeterInhalt(attrappe, 'POST', '/api/quizze/21/abgabe/')).toEqual({
      antworten: [
        { frage: 31, antwort: 41 },
        { frage: 32, antwort: 44 },
      ],
    })
  })

  it('setzt das Quiz mit „Nochmal versuchen“ zurück', async () => {
    mockeApi(lektionsRouten())
    renderMitProvidern(<App />, { pfad: '/lektionen/7' })
    await userEvent.click(await screen.findByLabelText('Mehrere Werte'))
    await userEvent.click(screen.getByLabelText('0'))
    await userEvent.click(screen.getByRole('button', { name: 'Antworten abgeben' }))

    await userEvent.click(await screen.findByRole('button', { name: 'Nochmal versuchen' }))

    expect(screen.queryByText('1 von 2 richtig')).not.toBeInTheDocument()
    expect(screen.getByLabelText('Mehrere Werte')).not.toBeChecked()
  })

  it('markiert den Abschnitt als gelesen und blättert weiter', async () => {
    const attrappe = mockeApi(lektionsRouten())
    renderMitProvidern(<App />, { pfad: '/lektionen/7' })

    await userEvent.click(await screen.findByRole('button', { name: 'Gelesen – weiter →' }))

    expect(await screen.findByRole('heading', { name: 'Schlüssel' })).toBeInTheDocument()
    expect(screen.getByText('Abschnitt 2 von 2')).toBeInTheDocument()
    expect(screen.queryByRole('region', { name: 'Quiz' })).not.toBeInTheDocument()
    expect(attrappe).toHaveBeenCalledWith(
      '/api/abschnitte/11/gelesen/',
      expect.objectContaining({ method: 'POST' }),
    )
  })

  it('zeigt gelesene Abschnitte im Fortschrittsbalken', async () => {
    mockeApi(
      lektionsRouten([
        {
          id: 1,
          abschnitt: 11,
          quiz: null,
          test: null,
          projektaufgabe: null,
          punkte: null,
          max_punkte: null,
          erledigt_am: '2026-11-03T10:00:00Z',
        },
      ]),
    )
    renderMitProvidern(<App />, { pfad: '/lektionen/7' })

    await waitFor(() => {
      expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '1')
    })
    expect(screen.getByText('1 von 2 Abschnitten gelesen')).toBeInTheDocument()
    expect(screen.getByText('✓ gelesen')).toBeInTheDocument()
  })

  it('meldet eine ungültige Lektions-Adresse, ohne die API zu fragen', () => {
    const attrappe = mockeApi({})
    renderMitProvidern(<App />, { pfad: '/lektionen/abc' })

    expect(screen.getByRole('alert')).toHaveTextContent('Ungültige Lektion.')
    expect(attrappe).not.toHaveBeenCalledWith(
      expect.stringContaining('/api/lektionen/'),
      expect.anything(),
    )
  })

  it('schließt die Lektion am letzten Abschnitt ab', async () => {
    const gelesen = (abschnitt: number) => ({
      id: abschnitt,
      abschnitt,
      quiz: null,
      test: null,
      projektaufgabe: null,
      punkte: null,
      max_punkte: null,
      erledigt_am: '2026-11-03T10:00:00Z',
    })
    const attrappe = mockeApi({
      ...lektionsRouten([gelesen(11), gelesen(12)]),
      'POST /api/abschnitte/12/gelesen/': { json: gelesen(12) },
    })
    renderMitProvidern(<App />, { pfad: '/lektionen/7?abschnitt=2' })

    await userEvent.click(await screen.findByRole('button', { name: 'Lektion abschließen' }))

    expect(await screen.findByRole('status')).toHaveTextContent('Lektion abgeschlossen.')
    expect(attrappe).toHaveBeenCalledWith(
      '/api/abschnitte/12/gelesen/',
      expect.objectContaining({ method: 'POST' }),
    )
  })

  it('meldet, wenn „gelesen“ nicht gespeichert werden konnte', async () => {
    mockeApi({
      ...lektionsRouten(),
      'POST /api/abschnitte/11/gelesen/': { status: 500, json: {} },
    })
    renderMitProvidern(<App />, { pfad: '/lektionen/7' })

    await userEvent.click(await screen.findByRole('button', { name: 'Gelesen – weiter →' }))

    expect(
      await screen.findByText('Der Fortschritt konnte nicht gespeichert werden.'),
    ).toBeInTheDocument()
    expect(screen.getByText('Abschnitt 1 von 2')).toBeInTheDocument()
  })

  it('meldet eine fehlgeschlagene Quiz-Abgabe', async () => {
    mockeApi({
      ...lektionsRouten(),
      'POST /api/quizze/21/abgabe/': { status: 400, json: { detail: 'Ungültige Abgabe.' } },
    })
    renderMitProvidern(<App />, { pfad: '/lektionen/7' })
    await userEvent.click(await screen.findByLabelText('Mehrere Werte'))
    await userEvent.click(screen.getByLabelText('0'))
    await userEvent.click(screen.getByRole('button', { name: 'Antworten abgeben' }))

    expect(await screen.findByText(/Abgabe fehlgeschlagen: Ungültige Abgabe\./)).toBeInTheDocument()
  })

  it('meldet, wenn das Quiz nicht geladen werden kann', async () => {
    mockeApi({ ...lektionsRouten(), 'GET /api/quizze/21/': { status: 500, json: {} } })
    renderMitProvidern(<App />, { pfad: '/lektionen/7' })

    expect(await screen.findByText('Das Quiz konnte nicht geladen werden.')).toBeInTheDocument()
  })

  it('zeigt eine unsichere Quellen-Adresse nur als Text', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
    mockeApi({
      ...lektionsRouten(),
      'GET /api/lektionen/7/': {
        json: { ...LEKTION, quellen: [{ titel: 'Böse Quelle', url: 'javascript:alert(1)' }] },
      },
    })
    renderMitProvidern(<App />, { pfad: '/lektionen/7' })

    expect(await screen.findByText('Böse Quelle')).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'Böse Quelle' })).not.toBeInTheDocument()
  })
})
