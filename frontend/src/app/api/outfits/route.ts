import { NextResponse } from "next/server";

export async function GET(req: Request) {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/outfits`, {
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    });

    if (!res.ok) {
      throw new Error(`Backend error: ${res.status}`);
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (err: any) {
    console.error("❌ Error in /api/outfits:", err);
    return NextResponse.json({ error: "Failed to fetch outfits" }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/outfits`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      cache: "no-store"
    });

    if (!res.ok) {
      throw new Error(`Backend error: ${res.status}`);
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (err: any) {
    console.error("❌ Error in /api/outfits POST:", err);
    return NextResponse.json({ error: "Failed to create outfit" }, { status: 500 });
  }
}

// ===== OPTIONS HANDLER FOR CORS =====
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