import { renderHook, act } from '@testing-library/react';
import { useTheme } from '@/shared/hooks/ui/useTheme';

describe('useTheme', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Reset document class
    document.documentElement.classList.remove('light', 'dark');
  });

  it('should initialize with system theme when no theme is stored', () => {
    const { result } = renderHook(() => useTheme());
    expect(result.current.theme).toBe('system');
  });

  it('should initialize with stored theme from localStorage', () => {
    localStorage.setItem('theme', 'dark');
    const { result } = renderHook(() => useTheme());
    expect(result.current.theme).toBe('dark');
  });

  it('should update theme and store in localStorage', () => {
    const { result } = renderHook(() => useTheme());

    act(() => {
      result.current.setTheme('dark');
    });

    expect(result.current.theme).toBe('dark');
    expect(localStorage.getItem('theme')).toBe('dark');
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('should toggle between light and dark themes', () => {
    const { result } = renderHook(() => useTheme());

    act(() => {
      result.current.setTheme('light');
    });

    expect(result.current.theme).toBe('light');
    expect(document.documentElement.classList.contains('light')).toBe(true);

    act(() => {
      result.current.toggleTheme();
    });

    expect(result.current.theme).toBe('dark');
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('should handle system theme changes', () => {
    const { result } = renderHook(() => useTheme());

    // Mock system theme change
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    act(() => {
      mediaQuery.matches = true;
      mediaQuery.dispatchEvent(new Event('change'));
    });

    expect(result.current.resolvedTheme).toBe('dark');
  });
}); 