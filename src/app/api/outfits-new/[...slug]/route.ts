import { NextRequest, NextResponse } from 'next/server';

// FORCE REBUILD: Timestamp 2025-08-24 21:00:00
// Catch-all route for /api/outfits-new/[...slug] to handle nested endpoints
async function handleProxy(req: NextRequest, params: { slug: string[] }) {
  console.log("🚀 FORCE REBUILD: Catch-all /api/outfits-new/[...slug] route HIT:", req.method, params?.slug);
  
  try {
    const path = params.slug.join('/');
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/outfits/${path}${req.nextUrl.search}`;
    
    console.log("🚀 FORCE REBUILD: Backend URL for catch-all:", backendUrl);
    console.log("🚀 FORCE REBUILD: HTTP Method:", req.method);
    console.log("🚀 FORCE REBUILD: Slug path:", path);

    const res = await fetch(backendUrl, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        ...(req.headers.get('authorization') && {
          Authorization: req.headers.get('authorization')!,
        }),
      },
      body: req.method !== 'GET' && req.method !== 'HEAD' ? await req.text() : undefined,
    });

    if (!res.ok) {
      console.error(`❌ FORCE REBUILD: Backend responded with: ${res.status} for ${req.method} /outfits/${path}`);
      return NextResponse.json({ error: `Backend error: ${res.status}` }, { status: res.status });
    }

    // try to parse as JSON; fallback to text
    const contentType = res.headers.get('content-type');
    const data =
      contentType && contentType.includes('application/json')
        ? await res.json()
        : await res.text();

    console.log("🚀 FORCE REBUILD: Successfully fetched data from backend for:", path);
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error(`❌ FORCE REBUILD: Proxy ${req.method} /outfits-new/${params.slug.join('/')} failed:`, err);
    return NextResponse.json({ 
      error: 'Proxy failed', 
      details: err instanceof Error ? err.message : 'Unknown error',
      path: params.slug.join('/'),
      method: req.method
    }, { status: 500 });
  }
}

export async function GET(req: NextRequest, { params }: { params: { slug: string[] } }) {
  return handleProxy(req, params);
}

export async function POST(req: NextRequest, { params }: { params: { slug: string[] } }) {
  return handleProxy(req, params);
}

export async function PUT(req: NextRequest, { params }: { params: { slug: string[] } }) {
  return handleProxy(req, params);
}

export async function DELETE(req: NextRequest, { params }: { params: { slug: string[] } }) {
  return handleProxy(req, params);
}
