import { proxyToBackend } from '@/lib/server/backendProxy';

export const PUT = async (request: Request, { params }: { params: Promise<{ id: string }> }) =>
  proxyToBackend(request, '/api/outfits/' + encodeURIComponent((await params).id));
