import { NextResponse } from 'next/server';
import { proxyToBackend } from '@/lib/server/backendProxy';

export const dynamic = 'force-dynamic';
export const maxDuration = 60;

const respond = (body: unknown, status = 200) => NextResponse.json(body, {
  status, headers: { 'Cache-Control': 'private, no-store' },
});
const failure = (status: number) => respond({ success: false, error: 'Your item was not confirmed saved. Please retry.' }, status);

export async function GET(request: Request) {
  const countOnly = new URL(request.url).searchParams.get('count_only') === 'true';
  // Query the saved wardrobe so stale profile counts cannot complete a capsule.
  return proxyToBackend(request, `/api/wardrobe/${countOnly ? '?count_only=true' : ''}`, {
    method: 'GET', timeoutMs: 45_000,
  });
}

export async function POST(request: Request) {
  const parts = (request.headers.get('authorization') || '').trim().split(/\s+/);
  if (parts.length !== 2 || parts[0].toLowerCase() !== 'bearer' || !parts[1] || parts[1].toLowerCase() === 'test') return failure(401);
  let body: Record<string, unknown>;
  try {
    body = await request.json();
    if (!body || typeof body !== 'object' || Array.isArray(body)) return failure(400);
  } catch { return failure(400); }

  // The API verifies identity and rejects mismatched aliases; the proxy must
  // never replace an unverified caller's UID or silently strip a spoofed one.
  const response = await proxyToBackend(request, '/api/wardrobe/add-direct', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body), timeoutMs: 45_000,
  });
  if (!response.ok) return failure(response.status >= 400 && response.status <= 599 ? response.status : 502);
  let saved: any;
  try { saved = await response.json(); } catch { return failure(502); }
  const item = saved?.item;
  if (saved?.success !== true || typeof item?.id !== 'string' || !item.id.trim() ||
    typeof item.userId !== 'string' || !item.userId.trim() ||
    ['user_id', 'firebase_uid'].some(key => item[key] != null && item[key] !== item.userId) ||
    (typeof body.id === 'string' && body.id !== item.id) ||
    ['userId', 'user_id', 'firebase_uid'].some(key => body[key] != null && body[key] !== item.userId)) return failure(502);
  return respond(saved);
}
