import { NextResponse } from 'next/server';

// Legacy Clerk writer retired. Firebase-authenticated profile APIs own account updates.
export async function POST() {
  return NextResponse.json({ error: 'Not found' }, { status: 404 });
}
