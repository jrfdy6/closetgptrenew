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
        className="p-2 rounded-2xl bg-white/60 dark:bg-[#1A1A1A]/70 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 backdrop-blur transition-colors"
        aria-label="Loading theme toggle"
      >
        <div className="w-4 h-4 bg-[#FFB84C]/40 dark:bg-[#FF9400]/40 rounded animate-pulse" />
      </button>
    );
  }

  const isDark = resolvedTheme === 'dark';

  return (
    <button
      data-testid="theme-toggle"
      onClick={handleThemeChange}
      className="p-2 rounded-2xl bg-white/60 dark:bg-[#1A1A1A]/70 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 backdrop-blur transition-all duration-200 hover:scale-[1.03] shadow-sm shadow-amber-500/10"
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} theme`}
    >
      {isDark ? (
        <Sun className="w-4 h-4 text-[#FFB84C]" />
      ) : (
        <Moon className="w-4 h-4 text-[#FF9400]" />
      )}
    </button>
  );
};

export default ThemeToggle; 