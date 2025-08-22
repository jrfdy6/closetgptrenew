import { NextResponse } from "next/server";

export async function GET(req: Request) {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/outfit-history/today`, {
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    });

    if (!res.ok) {
      throw new Error(`Backend error: ${res.status}`);
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (err: any) {
    console.error("❌ Error in /api/outfit-history/today:", err);
    return NextResponse.json({ error: "Failed to fetch today's outfit" }, { status: 500 });
  }
}
