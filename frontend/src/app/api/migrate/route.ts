import { NextResponse } from 'next/server';

// Bulk schema migrations belong in authenticated operator scripts, never HTTP.
export async function POST() {
  return NextResponse.json({ error: 'Not found' }, { status: 404 });
}
