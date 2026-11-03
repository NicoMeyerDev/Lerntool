/**
 * Typen für die Umgebungsvariablen des Frontends (siehe `.env.example`).
 */
interface ImportMetaEnv {
  /** Basis-URL des Backends, z. B. `https://api.example.org`. Leer: gleicher Host. */
  readonly VITE_API_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
