/**
 * Dashboard auf der Startseite: Level und XP, Statistiken, Fortschritt je Thema,
 * Abzeichen und Meilensteine. Alle Werte berechnet das Backend; hier wird nur dargestellt.
 */
import { useDashboard } from '../api/lernen'
import type { Dashboard } from '../api/schemas'
import { Fortschrittsbalken } from './Fortschrittsbalken'
import { Fehler, Laden } from './Zustand'

/**
 * Eine Kennzahl als kleine Karte.
 *
 * @param props.wert - Der große Wert.
 * @param props.beschriftung - Erklärender Text darunter.
 * @returns Die Karte.
 */
function Kennzahl({ wert, beschriftung }: { wert: string; beschriftung: string }) {
  return (
    <div className="rounded-card border border-border bg-surface p-4">
      <p className="text-2xl font-extrabold text-accent-cyan">{wert}</p>
      <p className="mt-1 text-sm text-text-muted">{beschriftung}</p>
    </div>
  )
}

/**
 * Level-Karte mit XP-Balken bis zum nächsten Level.
 *
 * @param props.dashboard - Die Dashboard-Daten.
 * @returns Die Level-Karte.
 */
function LevelKarte({ dashboard }: { dashboard: Dashboard }) {
  return (
    <div className="rounded-card border border-accent-violet/50 bg-accent-violet/10 p-5">
      <p className="text-sm font-semibold tracking-wide text-accent-violet uppercase">Level</p>
      <p className="text-4xl font-extrabold">{dashboard.level}</p>
      <div className="mt-3">
        <Fortschrittsbalken
          aktuell={dashboard.xp_im_level}
          gesamt={dashboard.xp_pro_level}
          beschriftung={`${String(dashboard.xp_im_level)} von ${String(dashboard.xp_pro_level)} XP bis Level ${String(dashboard.level + 1)}`}
        />
      </div>
      <p className="mt-2 text-sm text-text-muted">Insgesamt {dashboard.xp} XP</p>
    </div>
  )
}

/**
 * Das komplette Dashboard.
 *
 * @param props.dashboard - Die Dashboard-Daten.
 * @returns Level, Kennzahlen, Themenfortschritt, Meilensteine und Abzeichen.
 */
function DashboardInhalt({ dashboard }: { dashboard: Dashboard }) {
  const { statistik } = dashboard
  return (
    <div className="space-y-6">
      <LevelKarte dashboard={dashboard} />

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Kennzahl
          wert={`${String(statistik.abschnitte_gelesen)}/${String(statistik.abschnitte_gesamt)}`}
          beschriftung="Abschnitte gelesen"
        />
        <Kennzahl
          wert={`${String(statistik.quizze_bearbeitet)}/${String(statistik.quizze_gesamt)}`}
          beschriftung="Quizze bearbeitet"
        />
        <Kennzahl
          wert={`${String(statistik.tests_bearbeitet)}/${String(statistik.tests_gesamt)}`}
          beschriftung="Tests bearbeitet"
        />
        <Kennzahl
          wert={`${String(statistik.projekte_erledigt)}/${String(statistik.projekte_gesamt)}`}
          beschriftung="Projekte erledigt"
        />
      </div>
      <p className="text-text-muted">
        Trefferquote:{' '}
        <strong className="text-text">
          {statistik.trefferquote_prozent === null
            ? 'noch kein Ergebnis'
            : `${String(statistik.trefferquote_prozent)} %`}
        </strong>
      </p>

      {dashboard.themen.length > 0 && (
        <section aria-labelledby="themenfortschritt" className="space-y-3">
          <h2 id="themenfortschritt" className="text-xl font-bold text-accent-violet">
            Fortschritt je Thema
          </h2>
          {dashboard.themen.map((thema) => (
            <Fortschrittsbalken
              key={thema.slug}
              aktuell={thema.erledigt}
              gesamt={thema.gesamt}
              beschriftung={`${thema.titel}: ${String(thema.erledigt)} von ${String(thema.gesamt)}`}
            />
          ))}
        </section>
      )}

      <section aria-labelledby="meilensteine" className="space-y-3">
        <h2 id="meilensteine" className="text-xl font-bold text-accent-violet">
          Meilensteine
        </h2>
        {dashboard.meilensteine.map((meilenstein) => (
          <Fortschrittsbalken
            key={meilenstein.schluessel}
            aktuell={Math.min(meilenstein.aktuell, meilenstein.ziel)}
            gesamt={meilenstein.ziel}
            beschriftung={`${meilenstein.titel}: ${String(meilenstein.aktuell)} von ${String(meilenstein.ziel)}${meilenstein.erreicht ? ' ✓' : ''}`}
          />
        ))}
      </section>

      <section aria-labelledby="abzeichen" className="space-y-3">
        <h2 id="abzeichen" className="text-xl font-bold text-accent-violet">
          Abzeichen
        </h2>
        <ul className="grid gap-3 sm:grid-cols-2">
          {dashboard.abzeichen.map((abzeichen) => (
            <li
              key={abzeichen.schluessel}
              className={`rounded-card border p-4 ${
                abzeichen.erreicht
                  ? 'border-success bg-success/10'
                  : 'border-border bg-surface text-text-muted'
              }`}
            >
              <p className="font-bold">
                <span aria-hidden="true">{abzeichen.erreicht ? '🏅' : '🔒'}</span> {abzeichen.titel}
              </p>
              <p className="text-sm">{abzeichen.beschreibung}</p>
              <p className="mt-1 text-sm font-semibold">
                {abzeichen.erreicht ? 'Erreicht' : 'Noch nicht erreicht'}
              </p>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}

/**
 * Lädt das Dashboard und zeigt es an.
 *
 * @returns Das Dashboard, einen Ladehinweis oder eine Fehlermeldung.
 */
export function DashboardUebersicht() {
  const dashboard = useDashboard()
  return (
    <section aria-label="Dein Fortschritt" className="space-y-4">
      <h2 className="text-2xl font-extrabold">Dein Fortschritt</h2>
      {dashboard.isPending && <Laden text="Fortschritt wird geladen …" />}
      {dashboard.isError && <Fehler text="Der Fortschritt konnte nicht geladen werden." />}
      {dashboard.isSuccess && <DashboardInhalt dashboard={dashboard.data} />}
    </section>
  )
}
