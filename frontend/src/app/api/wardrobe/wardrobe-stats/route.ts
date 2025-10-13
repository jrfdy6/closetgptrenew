import { NextResponse } from 'next/server';

export async function GET(req: Request) {
  try {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-production.up.railway.app';
    const res = await fetch(`${backendUrl}/api/wardrobe/wardrobe-stats`, {
      method: "GET", // ✅ explicitly GET
      headers: {
        Authorization: req.headers.get("authorization") || "",
      },
    });

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (err: any) {
    return NextResponse.json(
      { error: "Failed to fetch wardrobe stats", details: err.message },
      { status: 500 }
    );
  }
} 