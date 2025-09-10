import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({ 
    message: 'Test route working',
    timestamp: new Date().toISOString(),
    env: {
      NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
      NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL
    }
  });
}
