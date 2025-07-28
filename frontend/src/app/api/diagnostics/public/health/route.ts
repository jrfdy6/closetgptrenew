import { NextResponse } from 'next/server';

// Force dynamic rendering to prevent static generation
export const dynamic = 'force-dynamic';

export async function GET() {
  console.log("🏥 Returning mock health data");
  return NextResponse.json({
    status: "healthy",
    timestamp: Math.floor(Date.now() / 1000),
    environment: "production",
    version: "1.0.0",
    features: ["gpt4_vision", "wardrobe", "outfits", "weather", "analytics"],
    message: "Mock health data (backend not available during build)"
  });
} 