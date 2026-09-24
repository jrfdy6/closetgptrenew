import { proxyToBackend } from '@/lib/server/backendProxy';
export const dynamic = 'force-dynamic';
export const POST = (request: Request, { params }: { params: { id: string } }) => proxyToBackend(request, '/api/wardrobe/' + encodeURIComponent(params.id) + '/increment-wear', { forwardIdempotencyKey: true });
