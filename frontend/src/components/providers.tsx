'use client'

import { ThemeProvider } from 'next-themes'
import { FirebaseProvider } from '@/lib/firebase-context'
import { AuthProvider } from '@/contexts/AuthContext'
import { XPNotificationProvider } from '@/contexts/XPNotificationContext'

// Suppress harmless Cross-Origin-Opener-Policy warnings from Firebase OAuth popup
// This runs early to catch errors before Firebase loads
if (typeof window !== 'undefined' && !(window as any).__firebaseConsoleFilterSet) {
  const originalError = console.error;
  const originalWarn = console.warn;
  
  const shouldSuppress = (args: any[]): boolean => {
    const message = args.map(arg => 
      typeof arg === 'string' ? arg : 
      typeof arg === 'object' && arg !== null ? String(arg) : 
      String(arg)
    ).join(' ');
    
    return message.includes('Cross-Origin-Opener-Policy') || 
           message.includes('window.closed call') ||
           message.includes('COOP');
  };
  
  console.error = (...args: any[]) => {
    if (!shouldSuppress(args)) {
      originalError.apply(console, args);
    }
  };
  
  console.warn = (...args: any[]) => {
    if (!shouldSuppress(args)) {
      originalWarn.apply(console, args);
    }
  };
  
  (window as any).__firebaseConsoleFilterSet = true;
}

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <FirebaseProvider>
      <AuthProvider>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <XPNotificationProvider>
            {children}
          </XPNotificationProvider>
        </ThemeProvider>
      </AuthProvider>
    </FirebaseProvider>
  )
}
