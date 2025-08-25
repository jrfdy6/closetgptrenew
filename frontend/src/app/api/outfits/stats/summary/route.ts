import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  console.log("📊 [Frontend] /api/outfits/stats/summary GET route HIT");
  
  try {
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/outfits/stats/summary`;
    console.log("📊 [Frontend] Backend URL:", backendUrl);
    
    const res = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(req.headers.get('authorization') && {
          Authorization: req.headers.get('authorization')!,
        }),
      },
    });

    if (!res.ok) {
      console.error('❌ [Frontend] Backend responded with:', res.status);
      return NextResponse.json({ error: `Backend error: ${res.status}` }, { status: res.status });
    }

    const data = await res.json();
    console.log("✅ [Frontend] Successfully fetched stats from backend");
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error('❌ [Frontend] /api/outfits/stats/summary proxy failed:', err);
    return NextResponse.json({ error: 'Proxy failed', details: err instanceof Error ? err.message : 'Unknown error' }, { status: 500 });
  }
}
