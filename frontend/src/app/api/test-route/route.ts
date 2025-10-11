import { NextRequest, NextResponse } from 'next/server';

// Test route to verify API routes are working in Vercel
export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

export async function GET(request: NextRequest) {
  return NextResponse.json({ 
    success: true, 
    message: 'API routes are working!',
    timestamp: new Date().toISOString(),
    deployment: 'vercel-2025-10-11-v3'
  });
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  return NextResponse.json({ 
    success: true, 
    message: 'POST method is working!',
    receivedData: body,
    timestamp: new Date().toISOString(),
    deployment: 'vercel-2025-10-11-v3'
  });
}

