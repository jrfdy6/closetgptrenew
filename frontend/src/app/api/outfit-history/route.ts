import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  console.log("✅ /api/outfit-history route HIT:", req.method);
  
  try {
    // Use hardcoded Railway URL to ensure correct backend is called
    const backendUrl = 'https://closetgptrenew-production.up.railway.app';
    const fullBackendUrl = `${backendUrl}/api/outfit-history/${req.nextUrl.search}`;
    console.log("🔍 DEBUG: Backend URL:", fullBackendUrl);

    const res = await fetch(fullBackendUrl, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer test', // Use test token for development
      },
    });

    console.log("🔍 DEBUG: Backend response status:", res.status);
    console.log("🔍 DEBUG: Backend response ok:", res.ok);

    // try to parse as JSON; fallback to text
    const contentType = res.headers.get('content-type');
    const data =
      contentType && contentType.includes('application/json')
        ? await res.json()
        : await res.text();

    console.log("🔍 DEBUG: Backend response data:", data);

    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error(`❌ Proxy ${req.method} /outfit-history`, err);
    return NextResponse.json({ error: 'Failed to fetch outfit history' }, { status: 500 });
  }
}
