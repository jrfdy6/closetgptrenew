// lib/normalization.ts
export function normalizeArrayStrings(arr?: string[] | null): string[] {
  if (!Array.isArray(arr)) return [];
  return arr
    .map(s => (typeof s === "string" ? s.trim().toLowerCase() : ""))
    .filter(Boolean);
}

export function canonicalizeStyle(s: string): string {
  return s.trim().toLowerCase();
}

export function normalizeItemMetadata(item: any) {
  return {
    ...item,
    style: normalizeArrayStrings(item.style),
    occasion: normalizeArrayStrings(item.occasion),
    mood: normalizeArrayStrings(item.mood),
    // ensure season etc are normalized if used
    season: normalizeArrayStrings(item.season),
  };
}