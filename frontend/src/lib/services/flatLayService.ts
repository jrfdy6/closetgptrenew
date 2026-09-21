export interface FlatLayRequestResult {
  success: true;
  id: string;
  outfit_id: string;
  flat_lay_status: string;
  flat_lay_url: string | null;
  flat_lay_error: string | null;
  request_id: string | null;
  retryable: boolean;
  request_allowed: boolean;
  error_code?: string | null;
  credit_status?: string | null;
}

export async function requestFlatLay(outfitId: string, token: string): Promise<FlatLayRequestResult> {
  if (!outfitId || !token) throw new Error('Sign in and save this outfit before requesting a flat lay.');
  const response = await fetch(`/api/outfits/${encodeURIComponent(outfitId)}/flat-lay-request`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: '{}',
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const message = data?.error ?? data?.detail;
    throw new Error(typeof message === 'string' ? message : 'Could not confirm the flat lay request. Please try again.');
  }
  if (data?.success !== true || data?.id !== outfitId || typeof data?.flat_lay_status !== 'string') {
    throw new Error('Could not confirm the flat lay request. Please try again.');
  }
  return data;
}

export function flatLayRequestFields(result: FlatLayRequestResult) {
  return {
    flat_lay_status: result.flat_lay_status,
    flatLayStatus: result.flat_lay_status,
    flat_lay_url: result.flat_lay_url ?? null,
    flatLayUrl: result.flat_lay_url ?? null,
    flat_lay_error: result.flat_lay_error ?? null,
    flatLayError: result.flat_lay_error ?? null,
    flat_lay_request_allowed: result.request_allowed,
    flat_lay_request_id: result.request_id,
    flat_lay_retryable: result.retryable,
    flat_lay_error_code: result.error_code ?? null,
    flat_lay_credit_status: result.credit_status ?? null,
  };
}
