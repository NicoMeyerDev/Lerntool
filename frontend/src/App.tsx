/**
 * Wurzelkomponente: Routen der App.
 */
import { Link, Route, Routes } from 'react-router'

import { GeschuetzterBereich } from './components/Layout'
import { LektionSeite } from './pages/LektionSeite'
import { LoginSeite } from './pages/LoginSeite'
import { StartSeite } from './pages/StartSeite'
import { ThemaSeite } from './pages/ThemaSeite'

/**
 * Seite für unbekannte Adressen.
 *
 * @returns Hinweis mit Link zur Startseite.
 */
function NichtGefunden() {
  return (
    <main className="mx-auto max-w-3xl px-4 py-10">
      <h1 className="text-2xl font-bold">Seite nicht gefunden</h1>
      <Link to="/" className="mt-4 inline-block text-accent-cyan underline">
        Zur Startseite
      </Link>
    </main>
  )
}

/**
 * Legt fest, welche Seite zu welcher Adresse gehört. Alles außer `/login` braucht Anmeldung.
 *
 * @returns Die Routen.
 */
export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginSeite />} />
      <Route element={<GeschuetzterBereich />}>
        <Route index element={<StartSeite />} />
        <Route path="themen/:slug" element={<ThemaSeite />} />
        <Route path="lektionen/:id" element={<LektionSeite />} />
      </Route>
      <Route path="*" element={<NichtGefunden />} />
    </Routes>
  )
}
