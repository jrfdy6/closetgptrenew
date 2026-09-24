import { proxyToBackend } from '@/lib/server/backendProxy';

export const dynamic = 'force-dynamic';
export const GET = (request: Request) => {
  const query = new URL(request.url).searchParams;
  return proxyToBackend(request, '/api/outfits?' + query.toString());
};
export async function POST(request: Request) {
  let body: unknown;
  try { body = await request.json(); } catch {
    return Response.json({ success: false, error: 'Please check your outfit details.' }, { status: 422, headers: { 'Cache-Control': 'private, no-store' } });
  }
  const manual = body && typeof body === 'object' && 'items' in body && Array.isArray(body.items) && body.items.length > 0;
  return proxyToBackend(request, manual ? '/api/outfits/' : '/api/outfits/generate', { body: JSON.stringify(body), headers: { 'Content-Type': 'application/json' } });
}
