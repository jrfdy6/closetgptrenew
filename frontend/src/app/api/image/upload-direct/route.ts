import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

// Unused legacy endpoint. The supported upload path verifies identity and
// stores the original on Railway through /api/image/upload.
export async function POST() {
  return NextResponse.json({ success: false, error: 'Please use the current photo upload flow.' }, {
    status: 410, headers: { 'Cache-Control': 'private, no-store' },
  });
}
