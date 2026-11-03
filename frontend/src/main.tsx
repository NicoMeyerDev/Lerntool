/**
 * Einstiegspunkt des Frontends: bindet React, TanStack Query, Anmeldung, Router und Styles ein.
 */
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router'

import App from './App.tsx'
import { AuthProvider } from './auth/AuthProvider'
import './index.css'

const rootElement = document.getElementById('root')
if (rootElement === null) {
  throw new Error('Element #root fehlt in index.html.')
}

const queryClient = new QueryClient()

createRoot(rootElement).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  </StrictMode>,
)
