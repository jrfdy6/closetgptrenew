import type { NextRequest } from 'next/server';
import { proxyToBackend } from '@/lib/server/backendProxy';

export const runtime = 'nodejs';

export async function POST(request: NextRequest) {
  return proxyToBackend(request, '/api/style-quiz/submit');
}
