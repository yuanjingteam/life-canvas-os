import ReactDom from 'react-dom/client'
import React from 'react'
import { QueryClientProvider } from '@tanstack/react-query'

import { AppRoutes } from './routes'
import { AppProvider } from './contexts/AppContext'
import { Toaster } from './components/ui/sonner'
import { queryClient } from './lib/query-client'

import './globals.css'

ReactDom.createRoot(document.querySelector('app') as HTMLElement).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <AppProvider>
        <AppRoutes />
        <Toaster closeButton position="top-right" richColors />
      </AppProvider>
    </QueryClientProvider>
  </React.StrictMode>
)
