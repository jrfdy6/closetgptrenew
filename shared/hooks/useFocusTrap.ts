import { RefObject, useEffect, useCallback } from 'react';

export const useFocusTrap = (
  ref: RefObject<HTMLElement>,
  isActive: boolean = true
): void => {
  const getFocusableElements = useCallback((): HTMLElement[] => {
    if (!ref.current) return [];

    return Array.from(
      ref.current.querySelectorAll<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
    ).filter((el) => {
      const style = window.getComputedStyle(el);
      return (
        style.display !== 'none' &&
        style.visibility !== 'hidden' &&
        style.opacity !== '0' &&
        !el.hasAttribute('disabled') &&
        !el.hasAttribute('aria-hidden')
      );
    });
  }, [ref]);

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!isActive || !ref.current) return;

      const focusableElements = getFocusableElements();
      if (focusableElements.length === 0) return;

      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];
      const isTabPressed = event.key === 'Tab';

      if (!isTabPressed) return;

      if (event.shiftKey) {
        // If shift + tab
        if (document.activeElement === firstElement) {
          lastElement.focus();
          event.preventDefault();
        }
      } else {
        // If tab
        if (document.activeElement === lastElement) {
          firstElement.focus();
          event.preventDefault();
        }
      }
    },
    [isActive, ref, getFocusableElements]
  );

  useEffect(() => {
    if (!isActive || !ref.current) return;

    const focusableElements = getFocusableElements();
    if (focusableElements.length === 0) return;

    // Store the previously focused element
    const previousActiveElement = document.activeElement as HTMLElement;

    // Focus the first focusable element
    focusableElements[0].focus();

    // Add event listener for keyboard navigation
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      // Restore focus to the previously focused element
      previousActiveElement?.focus();
    };
  }, [isActive, ref, getFocusableElements, handleKeyDown]);
};

// Helper function to check if an element is focusable
export const isFocusable = (element: HTMLElement): boolean => {
  const tagName = element.tagName.toLowerCase();
  const tabIndex = element.getAttribute('tabindex');
  const disabled = element.hasAttribute('disabled');
  const hidden = element.hasAttribute('hidden');
  const ariaHidden = element.getAttribute('aria-hidden') === 'true';
  const style = window.getComputedStyle(element);

  return (
    (tagName === 'a' && element.hasAttribute('href')) ||
    (tagName === 'button' && !disabled) ||
    (tagName === 'input' && !disabled) ||
    (tagName === 'select' && !disabled) ||
    (tagName === 'textarea' && !disabled) ||
    (tabIndex !== null && tabIndex !== '-1') ||
    (!hidden && !ariaHidden && style.display !== 'none' && style.visibility !== 'hidden')
  );
};

// Helper function to get the next focusable element
export const getNextFocusableElement = (
  currentElement: HTMLElement,
  container: HTMLElement
): HTMLElement | null => {
  const focusableElements = Array.from(
    container.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
  ).filter(isFocusable);

  const currentIndex = focusableElements.indexOf(currentElement);
  return focusableElements[currentIndex + 1] || focusableElements[0];
};

// Helper function to get the previous focusable element
export const getPreviousFocusableElement = (
  currentElement: HTMLElement,
  container: HTMLElement
): HTMLElement | null => {
  const focusableElements = Array.from(
    container.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
  ).filter(isFocusable);

  const currentIndex = focusableElements.indexOf(currentElement);
  return focusableElements[currentIndex - 1] || focusableElements[focusableElements.length - 1];
}; 