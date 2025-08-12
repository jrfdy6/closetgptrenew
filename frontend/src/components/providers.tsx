'use client'

import { ThemeProvider } from 'next-themes'
import { FirebaseProvider } from '@/lib/firebase-context'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <FirebaseProvider>
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
        {children}
      </ThemeProvider>
    </FirebaseProvider>
  )
}
