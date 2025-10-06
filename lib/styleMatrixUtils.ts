// lib/styleMatrixUtils.ts
// Utility functions for working with the style compatibility matrix

import { STYLE_COMPATIBILITY } from './styleMatrix';

/**
 * Normalizes a style string to lowercase for consistent matching
 */
export function normalizeStyle(style: string): string {
  return style.trim().toLowerCase();
}

/**
 * Normalizes an array of style strings
 */
export function normalizeStyles(styles: string[]): string[] {
  return styles
    .map(style => normalizeStyle(style))
    .filter(style => style.length > 0);
}

/**
 * Gets compatible styles for a given style
 */
export function getCompatibleStyles(requestedStyle: string): string[] {
  const normalizedStyle = normalizeStyle(requestedStyle);
  return STYLE_COMPATIBILITY[normalizedStyle] || [];
}

/**
 * Checks if two styles are compatible
 */
export function areStylesCompatible(style1: string, style2: string): boolean {
  const normalizedStyle1 = normalizeStyle(style1);
  const normalizedStyle2 = normalizeStyle(style2);
  
  // Direct match
  if (normalizedStyle1 === normalizedStyle2) {
    return true;
  }
  
  // Check if style2 is in style1's compatibility list
  const compatibleStyles = getCompatibleStyles(normalizedStyle1);
  return compatibleStyles.includes(normalizedStyle2);
}

/**
 * Checks if a requested style matches any of the item's styles
 */
export function styleMatches(requestedStyle: string, itemStyles: string[]): boolean {
  if (!requestedStyle) return true;
  if (!itemStyles || itemStyles.length === 0) return true;
  
  const normalizedRequested = normalizeStyle(requestedStyle);
  const normalizedItemStyles = normalizeStyles(itemStyles);
  
  // Direct match
  if (normalizedItemStyles.includes(normalizedRequested)) {
    return true;
  }
  
  // Check compatibility matrix
  const compatibleStyles = getCompatibleStyles(normalizedRequested);
  return normalizedItemStyles.some(itemStyle => 
    compatibleStyles.includes(itemStyle)
  );
}

/**
 * Gets all available styles in the compatibility matrix
 */
export function getAllStyles(): string[] {
  return Object.keys(STYLE_COMPATIBILITY);
}

/**
 * Exports the style compatibility matrix in a normalized format
 * This ensures all keys and values are lowercase for consistent matching
 */
export function exportNormalizedStyleMatrix(): Record<string, string[]> {
  const normalized: Record<string, string[]> = {};
  
  for (const [key, values] of Object.entries(STYLE_COMPATIBILITY)) {
    const normalizedKey = normalizeStyle(key);
    const normalizedValues = normalizeStyles(values);
    normalized[normalizedKey] = normalizedValues;
  }
  
  return normalized;
}

/**
 * Validates that all styles in the matrix are properly normalized
 */
export function validateStyleMatrix(): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  for (const [key, values] of Object.entries(STYLE_COMPATIBILITY)) {
    // Check if key is lowercase
    if (key !== key.toLowerCase()) {
      errors.push(`Key "${key}" is not lowercase`);
    }
    
    // Check if values are lowercase
    for (const value of values) {
      if (value !== value.toLowerCase()) {
        errors.push(`Value "${value}" in key "${key}" is not lowercase`);
      }
    }
    
    // Check if key is in its own compatibility list
    if (!values.includes(key)) {
      errors.push(`Key "${key}" is not in its own compatibility list`);
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}
