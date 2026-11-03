/// <reference types="vitest/config" />
/**
 * Vite-Konfiguration der Lern-App: React, Tailwind, PWA, Entwicklungs-Proxy und Tests.
 */
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['icon.svg'],
      manifest: {
        name: 'Lerntool',
        short_name: 'Lerntool',
        description: 'Persönliche Lern-App mit Lektionen, Quizzen und Fortschritt.',
        lang: 'de',
        start_url: '/',
        display: 'standalone',
        background_color: '#0b0d17',
        theme_color: '#0b0d17',
        icons: [{ src: 'icon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any' }],
      },
    }),
  ],
  server: {
    // Leitet API-Aufrufe im Entwicklungsmodus an das lokale Django-Backend weiter.
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
})
