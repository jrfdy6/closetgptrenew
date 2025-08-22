import { NextResponse } from "next/server";

export async function GET(req: Request) {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/outfits/stats/summary`, {
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    });

    if (!res.ok) {
      throw new Error(`Backend error: ${res.status}`);
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (err: any) {
    console.error("❌ Error in /api/outfits/stats/summary:", err);
    return NextResponse.json({ error: "Failed to get outfit statistics" }, { status: 500 });
  }
}
