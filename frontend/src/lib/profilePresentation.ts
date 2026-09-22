/** Profile dates historically arrive as ISO strings, epoch values, or Firestore JSON. */
function profileDate(value: unknown): Date | null {
  if (value === null || value === undefined || value === '') return null;
  let date: Date;
  if (value instanceof Date) {
    date = value;
  } else if (typeof value === 'number' || (typeof value === 'string' && /^\d+(?:\.\d+)?$/.test(value.trim()))) {
    const timestamp = Number(value);
    if (!Number.isFinite(timestamp) || timestamp <= 0) return null;
    date = new Date(timestamp < 100_000_000_000 ? timestamp * 1000 : timestamp);
  } else if (typeof value === 'string') {
    date = new Date(value);
  } else if (typeof value === 'object') {
    const timestamp = value as { seconds?: unknown; _seconds?: unknown };
    const seconds = timestamp.seconds ?? timestamp._seconds;
    if (typeof seconds !== 'number' || !Number.isFinite(seconds) || seconds <= 0) return null;
    date = new Date(seconds * 1000);
  } else {
    return null;
  }
  return Number.isFinite(date.getTime()) && date.getTime() > 0 ? date : null;
}

export function formatProfileDate(...values: unknown[]): string {
  for (const value of values) {
    const date = profileDate(value);
    if (date) return date.toLocaleDateString();
  }
  return 'Not available';
}
