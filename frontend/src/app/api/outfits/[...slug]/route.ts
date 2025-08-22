import { NextRequest, NextResponse } from 'next/server';

async function handleProxy(req: NextRequest, params: { slug: string[] }) {
  try {
    const path = params.slug.join('/');
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}/outfits/${path}${req.nextUrl.search}`;

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

    // try to parse as JSON; fallback to text
    const contentType = res.headers.get('content-type');
    const data =
      contentType && contentType.includes('application/json')
        ? await res.json()
        : await res.text();

    return NextResponse.json(data, { status: res.status });
  } catch (err) {
    console.error(`❌ Proxy ${req.method} /outfits/${params.slug.join('/')}`, err);
    return NextResponse.json({ error: 'Proxy failed' }, { status: 500 });
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
