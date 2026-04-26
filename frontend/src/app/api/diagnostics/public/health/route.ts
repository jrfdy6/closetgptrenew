import { NextResponse } from 'next/server';
import { serverDebugLog } from '@/lib/server/debug';

// Force dynamic rendering to prevent static generation
export const dynamic = 'force-dynamic';

export async function GET() {
  serverDebugLog('🏥 Returning mock health data');
  return NextResponse.json({
    status: "healthy",
    timestamp: Math.floor(Date.now() / 1000),
    environment: "production",
    version: "1.0.0",
    features: ["gpt4_vision", "wardrobe", "outfits", "weather", "analytics"],
    message: "Mock health data (backend not available during build)"
  });
} 
