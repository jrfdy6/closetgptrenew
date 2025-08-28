import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  console.log("🔍 [API] /api/outfits/stats GET route called");
  
  try {
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/outfits/stats/summary`;
    console.log("🔍 [API] Proxying to backend URL:", backendUrl);
    
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
      console.error('❌ [API] Backend responded with:', res.status);
      return NextResponse.json({ error: `Backend error: ${res.status}` }, { status: res.status });
    }

    const data = await res.json();
    console.log("✅ [API] Successfully fetched stats from backend");
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error('❌ [API] /api/outfits/stats proxy failed:', err);
    return NextResponse.json({ error: 'Proxy failed', details: err instanceof Error ? err.message : 'Unknown error' }, { status: 500 });
  }
}
