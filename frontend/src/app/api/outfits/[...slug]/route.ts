import { NextRequest, NextResponse } from 'next/server';

// FRESH IMPLEMENTATION - Catch-all route recreated to fix Vercel build issue
async function handleProxy(req: NextRequest, params: { slug: string[] }) {
  console.log("✅ FRESH: Catch-all /api/outfits/[...slug] route HIT:", req.method, params?.slug);
  
  try {
    const path = params.slug.join('/');
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/outfits/${path}${req.nextUrl.search}`;
    
    console.log("✅ FRESH: Backend URL for catch-all:", backendUrl);
    console.log("✅ FRESH: HTTP Method:", req.method);
    console.log("✅ FRESH: Slug path:", path);

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
      console.error(`❌ FRESH: Backend responded with: ${res.status} for ${req.method} /outfits/${path}`);
      return NextResponse.json({ error: `Backend error: ${res.status}` }, { status: res.status });
    }

    // try to parse as JSON; fallback to text
    const contentType = res.headers.get('content-type');
    const data =
      contentType && contentType.includes('application/json')
        ? await res.json()
        : await res.text();

    console.log("✅ FRESH: Successfully fetched data from backend for:", path);
    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error(`❌ FRESH: Proxy ${req.method} /outfits/${params.slug.join('/')} failed:`, err);
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
