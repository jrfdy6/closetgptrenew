/**
 * Safely formats a date value, handling various input types
 */
export function formatLastWorn(lastWorn: any): string {
  if (!lastWorn) {
    return 'Never worn';
  }
  
  // If it's already a Date object
  if (lastWorn instanceof Date) {
    return lastWorn.toLocaleDateString();
  }
  
  // If it's a timestamp (number)
  if (typeof lastWorn === 'number') {
    return new Date(lastWorn).toLocaleDateString();
  }
  
  // If it's a string, try to parse it
  if (typeof lastWorn === 'string') {
    const parsedDate = new Date(lastWorn);
    if (!isNaN(parsedDate.getTime())) {
      return parsedDate.toLocaleDateString();
    }
  }
  
  // If it's a Firestore timestamp object
  if (lastWorn && typeof lastWorn === 'object' && lastWorn.toDate) {
    return lastWorn.toDate().toLocaleDateString();
  }
  
  // Fallback
  return 'Unknown';
}

/**
 * Safely converts any date-like value to a Date object
 */
export function safeToDate(value: any): Date | null {
  if (!value) {
    return null;
  }
  
  if (value instanceof Date) {
    return value;
  }
  
  if (typeof value === 'number') {
    return new Date(value);
  }
  
  if (typeof value === 'string') {
    const parsed = new Date(value);
    return !isNaN(parsed.getTime()) ? parsed : null;
  }
  
  if (value && typeof value === 'object' && value.toDate) {
    return value.toDate();
  }
  
  return null;
}
