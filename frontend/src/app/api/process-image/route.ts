import { NextResponse } from 'next/server';
export const dynamic = 'force-dynamic';
export async function POST() {
  return NextResponse.json({ success: false, error: 'This legacy endpoint is no longer available. Use the existing onboarding and wardrobe upload flow.' }, { status: 410, headers: { 'Cache-Control': 'private, no-store' } });
}
