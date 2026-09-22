import { NextRequest, NextResponse } from 'next/server';
import { getBackendUrl } from '@/lib/server/backendUrl';

export const dynamic = 'force-dynamic';
const headers = { 'Cache-Control': 'private, no-store' };

export async function POST(request: NextRequest, { params }: { params: { id: string } }) {
  const authorization = request.headers.get('authorization');
  if (!authorization || !/^Bearer \S+$/.test(authorization)) return NextResponse.json({ success: false, error: 'Sign in to record a wear.' }, { status: 401, headers });
  const raw = await request.text();
  let body: { idempotency_key?: string; timezone?: string } | null = null;
  try { body = raw ? JSON.parse(raw) : null; } catch { /* rejected below */ }
  const legacy = raw.length === 0;
  if (!legacy && (typeof body?.idempotency_key !== 'string' || !body.idempotency_key.trim() || body.idempotency_key.length > 128)) {
    return NextResponse.json({ success: false, error: 'A wear operation identifier is required.' }, { status: 422, headers });
  }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(getBackendUrl().replace(/\/$/, '') + '/api/outfits/' + encodeURIComponent(params.id) + '/worn', {
      method: 'POST', cache: 'no-store', signal: controller.signal,
      headers: { Authorization: authorization, 'Content-Type': 'application/json' },
      ...(legacy ? {} : { body: JSON.stringify({ idempotency_key: body!.idempotency_key, timezone: body!.timezone || 'UTC' }) }),
    });
    const result = await response.json().catch(() => null);
    if (!response.ok) return NextResponse.json({ success: false, error: response.status === 404 ? 'This saved outfit is unavailable.' : response.status === 409 ? 'The pieces in this outfit are unavailable. Open a current outfit to record a wear.' : 'We could not confirm the wear record. Retry the same action.' }, { status: response.status, headers });
    if (result?.success !== true || result.outfit_id !== params.id || typeof result.event_id !== 'string' || !result.event_id.trim() || !Number.isInteger(result.wear_count) || result.wear_count < 0) {
      return NextResponse.json({ success: false, error: 'The wear response could not be confirmed. Retry the same action.' }, { status: 502, headers });
    }
    return NextResponse.json(result, { headers });
  } catch {
    return NextResponse.json({ success: false, error: 'The wear record may have saved. Retry to check the same action.' }, { status: 503, headers });
  } finally { clearTimeout(timer); }
}
