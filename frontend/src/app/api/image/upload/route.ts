import { NextResponse } from 'next/server';
import { proxyToBackend } from '@/lib/server/backendProxy';

export const dynamic = 'force-dynamic';
export const maxDuration = 60;

export async function POST(request: Request) {
  const parts = (request.headers.get('authorization') || '').trim().split(/\s+/);
  if (parts.length !== 2 || parts[0].toLowerCase() !== 'bearer' || !parts[1] || parts[1].toLowerCase() === 'test') {
    return NextResponse.json({ success: false, error: 'Please sign in to upload a photo.' }, {
      status: 401, headers: { 'Cache-Control': 'private, no-store' },
    });
  }
  let body: FormData;
  try { body = await request.formData(); } catch {
    return NextResponse.json({ success: false, error: 'The photo upload is invalid.' }, {
      status: 400, headers: { 'Cache-Control': 'private, no-store' },
    });
  }
  // Preserve multipart bytes and fields. Railway verifies the bearer token and
  // rejects ownership overrides before writing an original to Storage.
  return proxyToBackend(request, '/api/image/upload', { method: 'POST', body, timeoutMs: 45_000 });
}
