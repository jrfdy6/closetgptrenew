import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

function internalDebugRoutesEnabled() {
  return process.env.NODE_ENV !== 'production' || process.env.ENABLE_INTERNAL_DEBUG_PAGES === 'true';
}

export function middleware(request: NextRequest) {
  if (internalDebugRoutesEnabled()) {
    return NextResponse.next();
  }

  return new NextResponse('Not Found', { status: 404 });
}

export const config = {
  matcher: [
    '/dark-mode-test',
    '/debug-token',
    '/debug-wardrobe',
    '/debug/:path*',
    '/personalization-demo',
    '/personalization-demo-debug',
    '/test',
    '/test-flatlay',
    '/test-personalization',
    '/api/debug-stats',
    '/api/admin/:path*',
    '/api/analytics/diagnostics/:path*',
    '/api/debug/:path*',
    '/api/diagnostics/public/:path*',
    '/api/outfit-history/debug-user-docs',
    '/api/outfit-history/seed-test-data',
    '/api/outfit-history/verify-calculation',
    '/api/outfits/debug-filter',
    '/api/test-auth',
    '/api/test-env',
    '/api/test-route',
  ],
};
