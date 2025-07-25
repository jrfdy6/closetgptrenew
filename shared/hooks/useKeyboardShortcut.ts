import { useEffect, useCallback } from 'react';

type KeyCombo = string | string[];
type Modifier = 'ctrl' | 'alt' | 'shift' | 'meta';
type KeyHandler = (event: KeyboardEvent) => void;

interface ShortcutOptions {
  ctrl?: boolean;
  alt?: boolean;
  shift?: boolean;
  meta?: boolean;
  preventDefault?: boolean;
  stopPropagation?: boolean;
}

export const useKeyboardShortcut = (
  keyCombo: KeyCombo,
  callback: KeyHandler,
  options: ShortcutOptions = {}
) => {
  const {
    ctrl = false,
    alt = false,
    shift = false,
    meta = false,
    preventDefault = true,
    stopPropagation = false,
  } = options;

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      const keys = Array.isArray(keyCombo) ? keyCombo : [keyCombo];
      const key = event.key.toLowerCase();

      // Check if the pressed key matches any of the specified keys
      const keyMatch = keys.some((k) => k.toLowerCase() === key);

      // Check if all required modifiers are pressed
      const modifierMatch =
        event.ctrlKey === ctrl &&
        event.altKey === alt &&
        event.shiftKey === shift &&
        event.metaKey === meta;

      if (keyMatch && modifierMatch) {
        if (preventDefault) {
          event.preventDefault();
        }
        if (stopPropagation) {
          event.stopPropagation();
        }
        callback(event);
      }
    },
    [keyCombo, callback, ctrl, alt, shift, meta, preventDefault, stopPropagation]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);
};

// Helper function to create a keyboard shortcut string
export const createShortcutString = (
  key: string,
  options: ShortcutOptions = {}
): string => {
  const { ctrl = false, alt = false, shift = false, meta = false } = options;
  const modifiers: string[] = [];

  if (ctrl) modifiers.push('Ctrl');
  if (alt) modifiers.push('Alt');
  if (shift) modifiers.push('Shift');
  if (meta) modifiers.push('⌘');

  return [...modifiers, key.toUpperCase()].join(' + ');
};

// Predefined shortcuts
export const SHORTCUTS = {
  SAVE: { key: 's', ctrl: true },
  NEW: { key: 'n', ctrl: true },
  OPEN: { key: 'o', ctrl: true },
  CLOSE: { key: 'w', ctrl: true },
  UNDO: { key: 'z', ctrl: true },
  REDO: { key: 'y', ctrl: true },
  CUT: { key: 'x', ctrl: true },
  COPY: { key: 'c', ctrl: true },
  PASTE: { key: 'v', ctrl: true },
  DELETE: { key: 'Delete' },
  SELECT_ALL: { key: 'a', ctrl: true },
  SEARCH: { key: 'f', ctrl: true },
  HELP: { key: '?', ctrl: true, shift: true },
  ESCAPE: { key: 'Escape' },
} as const; 