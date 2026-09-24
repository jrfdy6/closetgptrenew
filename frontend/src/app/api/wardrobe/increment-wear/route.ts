import { proxyToBackend } from '@/lib/server/backendProxy';
export const dynamic = 'force-dynamic';
export async function POST(request: Request) {
  const body = await request.json().catch(() => null);
  if (typeof body?.itemId !== 'string' || !body.itemId.trim()) return Response.json({ error: 'Item ID is required.' }, { status: 422, headers: { 'Cache-Control': 'private, no-store' } });
  return proxyToBackend(request, '/api/wardrobe/' + encodeURIComponent(body.itemId) + '/increment-wear', { body: null, forwardIdempotencyKey: true });
}
