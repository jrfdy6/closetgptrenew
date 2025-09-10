import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  console.log("✅ /api/outfit-history route HIT:", req.method);
  
  try {
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/outfit-history/${req.nextUrl.search}`;
    console.log("🔍 DEBUG: Backend URL:", backendUrl);
    console.log("🔍 DEBUG: Environment variable NEXT_PUBLIC_API_URL:", process.env.NEXT_PUBLIC_API_URL);

    const res = await fetch(backendUrl, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        ...(req.headers.get('authorization') && {
          Authorization: req.headers.get('authorization')!,
        }),
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
