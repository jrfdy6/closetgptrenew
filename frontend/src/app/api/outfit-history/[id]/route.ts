import { proxyToBackend } from '@/lib/server/backendProxy';

export const dynamic = 'force-dynamic';
const forward = (request: Request, { params }: { params: { id: string } }) =>
  proxyToBackend(request, '/api/outfit-history/' + encodeURIComponent(params.id));
export const PATCH = forward;
export const DELETE = forward;
