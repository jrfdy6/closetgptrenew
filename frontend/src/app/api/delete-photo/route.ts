import { NextResponse } from 'next/server';

// No active product caller uses this retired endpoint. Do not restore the old
// Clerk/Admin or migration implementation in the frontend runtime.
export async function DELETE(_request: Request) {
  return NextResponse.json({ error: 'This endpoint has been retired.' }, {
    status: 410, headers: { 'Cache-Control': 'private, no-store' },
  });
}
