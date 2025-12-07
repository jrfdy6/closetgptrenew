'use client';

import React from 'react';
import { useTheme } from 'next-themes';
import { Moon, Sun } from 'lucide-react';

const ThemeToggle: React.FC = () => {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, [resolvedTheme, theme]);

  const handleThemeChange = () => {
    try {
      const newTheme = theme === 'dark' ? 'light' : 'dark';
      setTheme(newTheme);
    } catch (error) {
      // No-op; theme switching is non-critical
    }
  };

  // Prevent hydration mismatch
  if (!mounted) {
    return (
      <button
        className="p-2 rounded-2xl bg-card/60 dark:bg-card/70 border border-border/60 dark:border-border/70 backdrop-blur transition-colors"
        aria-label="Loading theme toggle"
      >
        <div className="w-4 h-4 bg-primary/40 dark:bg-accent/40 rounded animate-pulse" />
      </button>
    );
  }

  const isDark = resolvedTheme === 'dark';

  return (
    <button
      data-testid="theme-toggle"
      onClick={handleThemeChange}
      className="p-2 rounded-2xl bg-card/60 dark:bg-card/70 border border-border/60 dark:border-border/70 backdrop-blur transition-all duration-200 hover:scale-[1.03] shadow-sm shadow-amber-500/10"
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} theme`}
    >
      {isDark ? (
        <Sun className="w-4 h-4 text-primary" />
      ) : (
        <Moon className="w-4 h-4 text-accent" />
      )}
    </button>
  );
};

export default ThemeToggle; 