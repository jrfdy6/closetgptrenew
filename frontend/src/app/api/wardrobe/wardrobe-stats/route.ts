import { NextResponse } from 'next/server';
import { getBackendUrl } from '@/lib/server/backendUrl';

export async function GET(req: Request) {
  try {
    const backendUrl = getBackendUrl();
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
