import { NextRequest, NextResponse } from 'next/server';
import { getBackendUrl } from '@/lib/server/backendUrl';
import { serverDebugLog } from '@/lib/server/debug';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  serverDebugLog("✅ /api/outfit-history route HIT:", req.method);
  
  try {
    const authHeader = req.headers.get('authorization') || 'Bearer test';
    const backendUrl = getBackendUrl();
    const fullBackendUrl = `${backendUrl}/api/outfit-history/${req.nextUrl.search}`;
    serverDebugLog("🔍 DEBUG: Backend URL:", fullBackendUrl);

    const res = await fetch(fullBackendUrl, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authHeader,
      },
    });

    serverDebugLog("🔍 DEBUG: Backend response status:", res.status);
    serverDebugLog("🔍 DEBUG: Backend response ok:", res.ok);

    // try to parse as JSON; fallback to text
    const contentType = res.headers.get('content-type');
    const data =
      contentType && contentType.includes('application/json')
        ? await res.json()
        : await res.text();

    serverDebugLog("🔍 DEBUG: Backend response data:", data);

    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error(`❌ Proxy ${req.method} /outfit-history`, err);
    return NextResponse.json({ error: 'Failed to fetch outfit history' }, { status: 500 });
  }
}
