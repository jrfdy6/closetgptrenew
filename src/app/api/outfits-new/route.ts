import { NextRequest, NextResponse } from 'next/server';

// FORCE REBUILD: Timestamp 2025-08-24 21:00:00
// Main /api/outfits-new route
export async function GET(req: NextRequest) {
  console.log("🚀 FORCE REBUILD: /api/outfits-new GET route HIT:", req.method);
  
  try {
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/outfits${req.nextUrl.search}`;
    console.log("🚀 FORCE REBUILD: Backend URL:", backendUrl);
    
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
      console.error('❌ FORCE REBUILD: Backend responded with:', res.status);
      return NextResponse.json({ error: `Backend error: ${res.status}` }, { status: res.status });
    }

    const data = await res.json();
    console.log("🚀 FORCE REBUILD: Successfully fetched data from backend");
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error('❌ FORCE REBUILD: /api/outfits-new proxy failed:', err);
    return NextResponse.json({ error: 'Proxy failed', details: err instanceof Error ? err.message : 'Unknown error' }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  console.log("🚀 FORCE REBUILD: /api/outfits-new POST route HIT:", req.method);
  
  try {
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/outfits`;
    const body = await req.text();
    
    console.log("🚀 FORCE REBUILD: POST to backend URL:", backendUrl);
    
    const res = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(req.headers.get('authorization') && {
          Authorization: req.headers.get('authorization')!,
        }),
      },
      body: body,
    });

    if (!res.ok) {
      console.error('❌ FORCE REBUILD: Backend POST responded with:', res.status);
      return NextResponse.json({ error: `Backend error: ${res.status}` }, { status: res.status });
    }

    const data = await res.json();
    console.log("🚀 FORCE REBUILD: Successfully posted data to backend");
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error('❌ FORCE REBUILD: /api/outfits-new POST proxy failed:', err);
    return NextResponse.json({ error: 'Proxy failed', details: err instanceof Error ? err.message : 'Unknown error' }, { status: 500 });
  }
}
