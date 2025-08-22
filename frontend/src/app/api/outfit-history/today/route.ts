import { NextResponse } from "next/server";

export async function GET() {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/outfit-history/today`, { cache: "no-store" });
  const data = await res.json();
  return NextResponse.json(data);
}
