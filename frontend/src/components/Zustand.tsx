/**
 * Einheitliche Anzeigen für Laden und Fehler.
 */

/**
 * Hinweis, dass Daten geladen werden.
 *
 * @param props.text - Optionaler Text, Standard „Lädt …“.
 * @returns Ein Statushinweis.
 */
export function Laden({ text = 'Lädt …' }: { text?: string }) {
  return (
    <p role="status" className="py-8 text-center text-text-muted">
      {text}
    </p>
  )
}

/**
 * Fehlermeldung in einer roten Box.
 *
 * @param props.text - Die Meldung.
 * @returns Eine Fehlerbox mit `role="alert"`.
 */
export function Fehler({ text }: { text: string }) {
  return (
    <p role="alert" className="rounded-card border border-danger/50 bg-danger/10 p-4 text-danger">
      {text}
    </p>
  )
}
