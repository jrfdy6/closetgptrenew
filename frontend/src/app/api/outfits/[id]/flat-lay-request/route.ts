import { NextRequest, NextResponse } from 'next/server';
import { getBackendUrl } from '@/lib/server/backendUrl';

export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest, { params }: { params: { id: string } }) {
  const authorization = request.headers.get('authorization');
  if (!authorization?.startsWith('Bearer ') || !authorization.slice(7).trim()) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(`${getBackendUrl()}/api/outfits/${encodeURIComponent(params.id)}/flat-lay-request`, {
      method: 'POST',
      headers: { Authorization: authorization, 'Content-Type': 'application/json' },
      body: '{}',
      signal: controller.signal,
    });
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      return NextResponse.json({ error: typeof data?.detail === 'string' ? data.detail : 'Could not request this flat lay.' }, { status: response.status });
    }
    if (data?.success !== true || data?.id !== params.id || typeof data?.flat_lay_status !== 'string') {
      return NextResponse.json({ error: 'The server did not confirm the request. Please try again.' }, { status: 502 });
    }
    return NextResponse.json(data);
  } catch (error) {
    const timedOut = error instanceof Error && error.name === 'AbortError';
    return NextResponse.json({ error: 'Could not confirm the request. Please try again; an active request will not use another credit.' }, { status: timedOut ? 504 : 502 });
  } finally {
    clearTimeout(timeout);
  }
}
