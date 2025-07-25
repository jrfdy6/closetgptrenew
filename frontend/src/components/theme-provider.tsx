'use client';

import * as React from 'react';
import { ThemeProvider as NextThemesProvider, type ThemeProviderProps } from 'next-themes';

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  React.useEffect(() => {
    console.log('ThemeProvider mounted with props:', props);
  }, [props]);

  return <NextThemesProvider {...props}>{children}</NextThemesProvider>;
} 