import { NextRequest, NextResponse } from 'next/server';

// COMPLETELY NEW ROUTE - Different name to force Vercel rebuild
export async function GET(req: NextRequest) {
  console.log("🚀 NEW ROUTE: /api/outfits-new GET route HIT:", req.method);
  
  try {
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/outfits${req.nextUrl.search}`;
    console.log("🚀 NEW ROUTE: Backend URL:", backendUrl);
    
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
      console.error('❌ NEW ROUTE: Backend responded with:', res.status);
      return NextResponse.json({ error: `Backend error: ${res.status}` }, { status: res.status });
    }

    const data = await res.json();
    console.log("🚀 NEW ROUTE: Successfully fetched data from backend");
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error('❌ NEW ROUTE: /api/outfits-new proxy failed:', err);
    return NextResponse.json({ error: 'Proxy failed', details: err instanceof Error ? err.message : 'Unknown error' }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  console.log("🚀 NEW ROUTE: /api/outfits-new POST route HIT:", req.method);
  
  try {
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/outfits`;
    const body = await req.text();
    
    console.log("🚀 NEW ROUTE: POST to backend URL:", backendUrl);
    
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
      console.error('❌ NEW ROUTE: Backend POST responded with:', res.status);
      return NextResponse.json({ error: `Backend error: ${res.status}` }, { status: res.status });
    }

    const data = await res.json();
    console.log("🚀 NEW ROUTE: Successfully posted data to backend");
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error('❌ NEW ROUTE: /api/outfits-new POST proxy failed:', err);
    return NextResponse.json({ error: 'Proxy failed', details: err instanceof Error ? err.message : 'Unknown error' }, { status: 500 });
  }
}
