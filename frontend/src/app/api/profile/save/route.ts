import { NextResponse } from 'next/server';
import { proxyProfile } from '@/lib/server/profileProxy';

export async function POST(request: Request) {
  const response = await proxyProfile(request, 'PUT');
  if (!response.ok) return response;
  return NextResponse.json({ success: true });
}
