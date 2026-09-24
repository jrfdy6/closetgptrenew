export interface FlatLaySource {
  metadata?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface FlatLayState {
  url: string | null;
  status: string;
  error: string | null;
  requestAllowed: boolean;
  admissionPaused?: boolean;
  admissionReason?: string | null;
}

// Canonical top-level values, including explicit clears, precede legacy aliases.
export function extractFlatLayState(source: FlatLaySource): FlatLayState {
  const metadata = source.metadata ?? {};
  const read = (snake: string, camel: string) =>
    [source[snake], source[camel], metadata[snake], metadata[camel]].find(value => value !== undefined);
  const rawUrl = read('flat_lay_url', 'flatLayUrl');
  const url = typeof rawUrl === 'string' && rawUrl.trim() ? rawUrl : null;
  const rawStatus = read('flat_lay_status', 'flatLayStatus');
  const rawError = read('flat_lay_error', 'flatLayError');
  const allowed = read('flat_lay_request_allowed', 'flatLayRequestAllowed');
  return {
    url,
    status: typeof rawStatus === 'string' ? rawStatus.toLowerCase() : url ? 'done' : 'awaiting_consent',
    error: typeof rawError === 'string' && rawError.trim() ? rawError : null,
    requestAllowed: allowed !== false && source.flat_lay_admission_paused !== true,
    admissionPaused: source.flat_lay_admission_paused === true,
    admissionReason: typeof source.flat_lay_admission_reason === 'string' ? source.flat_lay_admission_reason : null,
  };
}

export function validStylingScore(value: unknown): number | null {
  return typeof value === 'number' && Number.isFinite(value) && value >= 0 && value <= 1 ? value : null;
}
