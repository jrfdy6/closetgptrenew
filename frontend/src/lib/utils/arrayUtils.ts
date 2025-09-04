/**
 * Normalizes a value that can be either a single item or an array into an array
 * @param value - The value to normalize (can be T or T[])
 * @returns An array containing the value(s)
 */
export function normalizeArray<T>(value: T | T[] | undefined | null): T[] {
  if (value === undefined || value === null) {
    return [];
  }
  return Array.isArray(value) ? value : [value];
}

/**
 * Safely maps over a value that can be either a single item or an array
 * @param value - The value to map over (can be T or T[])
 * @param mapper - The mapping function to apply to each item
 * @returns An array of mapped values
 */
export function safeMap<T, U>(
  value: T | T[] | undefined | null,
  mapper: (item: T) => U
): U[] {
  return normalizeArray(value).map(mapper);
}

/**
 * Safely slices a value that can be either a single item or an array
 * @param value - The value to slice (can be T or T[])
 * @param start - Start index for slice
 * @param end - End index for slice (optional)
 * @returns A sliced array
 */
export function safeSlice<T>(
  value: T | T[] | undefined | null,
  start: number,
  end?: number
): T[] {
  return normalizeArray(value).slice(start, end);
}
