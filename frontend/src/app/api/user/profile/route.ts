import { proxyProfile } from '@/lib/server/profileProxy';

export const dynamic = 'force-dynamic';
export const maxDuration = 60;
export const runtime = 'nodejs';

export const GET = (request: Request) => proxyProfile(request, 'GET');
export const POST = (request: Request) => proxyProfile(request, 'PUT');
export const PUT = POST;
