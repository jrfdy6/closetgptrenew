import { NextResponse } from 'next/server';
import { getBackendUrl } from '@/lib/server/backendUrl';
import { getFirebaseAdminAuth } from '@/lib/server/firebaseAdmin';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

const respond = (body: unknown, status = 200) => NextResponse.json(body, {
  status, headers: { 'Cache-Control': 'private, no-store' },
});
const failure = (status: number) => {
  const messages: Record<number, string> = {
    401: 'Please sign in again to retry photo preparation.',
    404: 'This wardrobe item is no longer available.',
    409: 'This photo cannot be retried in its current state. Refresh your capsule for the next step.',
    422: 'The retry request is invalid. Refresh your capsule and try again.',
    429: 'Please wait a moment before trying again.',
    502: 'The retry was not confirmed. Please try again; the same request will not restart processing twice.',
    503: 'Photo preparation is temporarily unavailable. Please try again.',
    504: 'The retry was not confirmed in time. Please try again; the same request will not restart processing twice.',
  };
  const safeStatus = messages[status] ? status : 502;
  return respond({ success: false, error: messages[safeStatus] }, safeStatus);
};
const invalidTokenCodes = new Set([
  'auth/argument-error', 'auth/invalid-id-token', 'auth/id-token-expired',
  'auth/id-token-revoked', 'auth/user-disabled', 'auth/user-not-found',
]);
const statuses = new Set(['pending', 'processing', 'done', 'failed', 'cancelled']);

export async function POST(request: Request, { params }: { params: { id: string } }) {
  const parts = (request.headers.get('authorization') || '').trim().split(/\s+/);
  if (parts.length !== 2 || parts[0].toLowerCase() !== 'bearer' || !parts[1] || parts[1].toLowerCase() === 'test') {
    return failure(401);
  }
  try {
    const decoded = await getFirebaseAdminAuth().verifyIdToken(parts[1], true);
    if (typeof decoded.uid !== 'string' || !decoded.uid.trim()) return failure(401);
  } catch (error) {
    const code = error && typeof error === 'object' && 'code' in error ? error.code : undefined;
    return failure(typeof code === 'string' && invalidTokenCodes.has(code) ? 401 : 503);
  }

  if (!/^[A-Za-z0-9_-][A-Za-z0-9_.-]{0,127}$/.test(params.id)) return failure(422);
  let body: unknown;
  try { body = await request.json(); } catch { return failure(422); }
  if (!body || typeof body !== 'object' || Array.isArray(body) ||
    Object.keys(body).length !== 1 || !('expected_attempt_id' in body) ||
    typeof body.expected_attempt_id !== 'string' || !body.expected_attempt_id.trim() ||
    body.expected_attempt_id.length > 256) return failure(422);

  // The backend derives ownership from this verified token and enforces the
  // failed-attempt fence. Never forward a client UID or processing projection.
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15_000);
  try {
    const response = await fetch(`${getBackendUrl()}/api/wardrobe/${encodeURIComponent(params.id)}/retry-processing`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${parts[1]}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ expected_attempt_id: body.expected_attempt_id }),
      cache: 'no-store', redirect: 'error', signal: controller.signal,
    });
    if (!response.ok) return failure(response.status);
    const data = await response.json();
    if (data?.success !== true || data.garment_id !== params.id || !statuses.has(data.status) ||
      typeof data.generation_id !== 'string' || !data.generation_id || data.generation_id.length > 256 ||
      !Number.isSafeInteger(data.attempt_count) || data.attempt_count < 0 || data.attempt_count > 3 ||
      typeof data.idempotent !== 'boolean') return failure(502);
    // Allowlist the acknowledgement; backend exception/debug fields never pass through.
    return respond({ success: true, garment_id: data.garment_id, status: data.status,
      generation_id: data.generation_id, attempt_count: data.attempt_count, idempotent: data.idempotent });
  } catch {
    return failure(controller.signal.aborted ? 504 : 502);
  } finally {
    clearTimeout(timeout);
  }
}
