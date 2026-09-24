import { NextResponse } from 'next/server';
export const dynamic = 'force-dynamic';
export async function GET() {
  return NextResponse.json({ success: false, error: 'This legacy feedback endpoint is no longer available.' }, { status: 410, headers: { 'Cache-Control': 'private, no-store' } });
}
