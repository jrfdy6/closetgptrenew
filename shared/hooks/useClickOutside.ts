import { RefObject, useEffect } from 'react';

type Event = MouseEvent | TouchEvent;

export const useClickOutside = <T extends HTMLElement = HTMLElement>(
  ref: RefObject<T>,
  handler: (event: Event) => void,
  mouseEvent: 'mousedown' | 'mouseup' = 'mousedown'
): void => {
  useEffect(() => {
    const listener = (event: Event) => {
      const el = ref?.current;
      const target = event.target as Node;

      // Do nothing if clicking ref's element or descendent elements
      if (!el || el.contains(target)) {
        return;
      }

      handler(event);
    };

    document.addEventListener(mouseEvent, listener);
    document.addEventListener('touchstart', listener);

    return () => {
      document.removeEventListener(mouseEvent, listener);
      document.removeEventListener('touchstart', listener);
    };
  }, [ref, handler, mouseEvent]);
};

// Helper function to check if a click is outside of multiple elements
export const isClickOutside = (
  event: Event,
  elements: (HTMLElement | null)[]
): boolean => {
  const target = event.target as Node;
  return !elements.some((el) => el?.contains(target));
};

// Helper function to get the closest parent element that matches a selector
export const getClosestParent = (
  element: HTMLElement,
  selector: string
): HTMLElement | null => {
  return element.closest(selector);
};

// Helper function to check if an element is a descendant of another element
export const isDescendant = (
  parent: HTMLElement,
  child: HTMLElement
): boolean => {
  let node: HTMLElement | null = child;
  while (node) {
    if (node === parent) {
      return true;
    }
    node = node.parentElement;
  }
  return false;
};

// Helper function to get all parent elements of an element
export const getParentElements = (element: HTMLElement): HTMLElement[] => {
  const parents: HTMLElement[] = [];
  let current: HTMLElement | null = element;

  while (current) {
    if (current.parentElement) {
      parents.push(current.parentElement);
    }
    current = current.parentElement;
  }

  return parents;
};

// Helper function to check if an element is visible
export const isElementVisible = (element: HTMLElement): boolean => {
  const style = window.getComputedStyle(element);
  return (
    style.display !== 'none' &&
    style.visibility !== 'hidden' &&
    style.opacity !== '0' &&
    element.offsetWidth > 0 &&
    element.offsetHeight > 0
  );
}; 