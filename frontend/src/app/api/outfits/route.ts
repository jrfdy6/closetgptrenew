import { NextRequest, NextResponse } from 'next/server';

// FORCE REBUILD: Timestamp 2025-08-24 21:00:00
// Main /api/outfits route
export async function GET(req: NextRequest) {
  console.log("🚀 FORCE REBUILD: /api/outfits GET route HIT:", req.method);
  console.log("🔍 DEBUG: Environment variables:", {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL
  });
  
  try {
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/outfits/${req.nextUrl.search}`;
    console.log("🚀 FORCE REBUILD: Backend URL:", backendUrl);
    console.log("🔍 DEBUG: Request URL search params:", req.nextUrl.search);
    console.log("🔍 DEBUG: Authorization header:", req.headers.get('authorization') ? 'Present' : 'Missing');
    
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
      console.error('❌ FORCE REBUILD: Backend responded with:', res.status, res.statusText);
      const errorText = await res.text().catch(() => 'Unable to read error response');
      console.error('❌ FORCE REBUILD: Backend error details:', errorText);
      return NextResponse.json({ 
        error: `Backend error: ${res.status} ${res.statusText}`, 
        details: errorText 
      }, { status: res.status });
    }

    const data = await res.json();
    console.log("🚀 FORCE REBUILD: Successfully fetched data from backend");
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error('❌ FORCE REBUILD: /api/outfits proxy failed:', err);
    console.error('❌ FORCE REBUILD: Error type:', typeof err);
    console.error('❌ FORCE REBUILD: Error details:', {
      message: err instanceof Error ? err.message : String(err),
      stack: err instanceof Error ? err.stack : undefined,
      cause: err instanceof Error ? err.cause : undefined
    });
    return NextResponse.json({ 
      error: 'Proxy failed', 
      details: err instanceof Error ? err.message : 'Unknown error',
      type: typeof err
    }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  console.log("🚀 FORCE REBUILD: /api/outfits POST route HIT:", req.method);
  
  try {
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/outfits/generate`;
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
    console.error('❌ FORCE REBUILD: /api/outfits POST proxy failed:', err);
    return NextResponse.json({ error: 'Proxy failed', details: err instanceof Error ? err.message : 'Unknown error' }, { status: 500 });
  }
}
