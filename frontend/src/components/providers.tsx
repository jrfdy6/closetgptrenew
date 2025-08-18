'use client'

import { ThemeProvider } from 'next-themes'
import { FirebaseProvider } from '@/lib/firebase-context'
import { AuthProvider } from '@/contexts/AuthContext'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <FirebaseProvider>
      <AuthProvider>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          {children}
        </ThemeProvider>
      </AuthProvider>
    </FirebaseProvider>
  )
}
