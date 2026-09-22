import { NextResponse } from 'next/server';

// This obsolete repair route bypassed quiz completion using an unverified JWT.
// Onboarding is completed through the authenticated quiz/profile flow only.
export async function POST() {
  return NextResponse.json({ error: 'Not found' }, { status: 404 });
}
