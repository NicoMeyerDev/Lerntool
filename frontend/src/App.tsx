/**
 * Startseite der Lern-App.
 */
import { HealthStatus } from './components/HealthStatus'

/**
 * Wurzelkomponente: Kopfbereich und Systemstatus.
 *
 * @returns Die Startseite.
 */
export default function App() {
  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-6 px-4 py-10">
      <header>
        <h1 className="bg-linear-to-r from-accent-cyan to-accent-violet bg-clip-text text-4xl font-extrabold text-transparent">
          Lerntool
        </h1>
        <p className="mt-2 text-text-muted">Deine persönliche Lern-App.</p>
      </header>
      <HealthStatus />
    </main>
  )
}
