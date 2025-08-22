import { NextRequest, NextResponse } from 'next/server';

// FRESH IMPLEMENTATION - Route recreated to fix Vercel build issue
export async function GET(req: NextRequest) {
  console.log("✅ FRESH: Direct /api/outfits route HIT:", req.method);
  
  try {
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/outfits${req.nextUrl.search}`;
    console.log("✅ FRESH: Backend URL:", backendUrl);
    
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
      console.error('❌ FRESH: Backend responded with:', res.status);
      return NextResponse.json({ error: `Backend error: ${res.status}` }, { status: res.status });
    }

    const data = await res.json();
    console.log("✅ FRESH: Successfully fetched data from backend");
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error('❌ FRESH: Direct /api/outfits proxy failed:', err);
    return NextResponse.json({ error: 'Proxy failed', details: err instanceof Error ? err.message : 'Unknown error' }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  console.log("✅ FRESH: Direct /api/outfits POST route HIT:", req.method);
  
  try {
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/outfits`;
    const body = await req.text();
    
    console.log("✅ FRESH: POST to backend URL:", backendUrl);
    
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
      console.error('❌ FRESH: Backend POST responded with:', res.status);
      return NextResponse.json({ error: `Backend error: ${res.status}` }, { status: res.status });
    }

    const data = await res.json();
    console.log("✅ FRESH: Successfully posted data to backend");
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error('❌ FRESH: Direct /api/outfits POST proxy failed:', err);
    return NextResponse.json({ error: 'Proxy failed', details: err instanceof Error ? err.message : 'Unknown error' }, { status: 500 });
  }
}

export async function OPTIONS(req: Request) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}
