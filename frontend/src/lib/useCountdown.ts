/**
 * Hook für einen Countdown in ganzen Sekunden.
 */
import { useEffect, useRef, useState } from 'react'

/**
 * Zählt ab dem Mounten von `sekunden` auf 0 herunter und ruft dann einmal `beiAblauf` auf.
 *
 * Die Startzeit gilt nur beim ersten Rendern; für einen neuen Countdown die Komponente
 * neu mounten (z. B. über `key`). Der Wert kommt vom Server, damit die Uhr des Geräts
 * keine Rolle spielt.
 *
 * @param sekunden - Startwert in Sekunden.
 * @param beiAblauf - Wird aufgerufen, sobald 0 erreicht ist.
 * @returns Die verbleibenden Sekunden.
 */
export function useCountdown(sekunden: number, beiAblauf: () => void): number {
  const [rest, setRest] = useState(sekunden)
  const ablaufRef = useRef(beiAblauf)

  useEffect(() => {
    ablaufRef.current = beiAblauf
  })

  useEffect(() => {
    const ende = Date.now() + sekunden * 1000
    const takt = window.setInterval(() => {
      const verbleibend = Math.max(0, Math.ceil((ende - Date.now()) / 1000))
      setRest(verbleibend)
      if (verbleibend === 0) {
        window.clearInterval(takt)
        ablaufRef.current()
      }
    }, 1000)
    return () => {
      window.clearInterval(takt)
    }
  }, [sekunden])

  return rest
}
