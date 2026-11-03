/**
 * Tests für die Statusanzeige (Health-Check).
 */
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { HealthStatus } from './HealthStatus'

/**
 * Rendert die Statusanzeige mit frischem Query-Client.
 */
function renderApp() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(
    <QueryClientProvider client={queryClient}>
      <HealthStatus />
    </QueryClientProvider>,
  )
}

describe('Systemstatus', () => {
  it('zeigt zunächst den Prüfzustand', () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() => new Promise<Response>(() => undefined)),
    )
    renderApp()

    expect(screen.getByRole('status')).toHaveTextContent('Verbindung wird geprüft')
  })

  it('meldet erreichbares Backend und Datenbank', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.resolve(Response.json({ status: 'ok', datenbank: 'ok' }))),
    )
    renderApp()

    expect(await screen.findByText('Backend und Datenbank erreichbar')).toBeInTheDocument()
  })

  it('meldet eine nicht erreichbare Datenbank bei 503', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() =>
        Promise.resolve(
          Response.json({ status: 'fehler', datenbank: 'nicht erreichbar' }, { status: 503 }),
        ),
      ),
    )
    renderApp()

    expect(await screen.findByText('Backend erreichbar, Datenbank nicht')).toBeInTheDocument()
  })

  it('meldet ein nicht erreichbares Backend', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.reject(new TypeError('Failed to fetch'))),
    )
    renderApp()

    expect(await screen.findByText('Backend nicht erreichbar')).toBeInTheDocument()
  })
})
