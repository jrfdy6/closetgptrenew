'use client';

import React from 'react';
import { useTheme } from 'next-themes';
import { Moon, Sun } from 'lucide-react';

const ThemeToggle: React.FC = () => {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
    console.log('ThemeToggle mounted, current theme:', theme, 'resolvedTheme:', resolvedTheme);
  }, [theme, resolvedTheme]);

  const handleThemeChange = () => {
    try {
      const newTheme = theme === 'dark' ? 'light' : 'dark';
      console.log('Changing theme from', theme, 'to', newTheme);
      setTheme(newTheme);
    } catch (error) {
      console.error('Error changing theme:', error);
    }
  };

  // Prevent hydration mismatch
  if (!mounted) {
    return (
      <button
        className="p-2 rounded-md bg-gray-100 dark:bg-gray-800 transition-colors hover:bg-gray-200 dark:hover:bg-gray-700"
        aria-label="Loading theme toggle"
      >
        <div className="w-4 h-4 bg-gray-300 dark:bg-gray-600 rounded animate-pulse" />
      </button>
    );
  }

  const isDark = resolvedTheme === 'dark';

  return (
    <button
      data-testid="theme-toggle"
      onClick={handleThemeChange}
      className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} theme`}
    >
      {isDark ? (
        <Sun className="w-4 h-4 text-gray-600 dark:text-gray-300" />
      ) : (
        <Moon className="w-4 h-4 text-gray-600 dark:text-gray-300" />
      )}
    </button>
  );
};

export default ThemeToggle; 