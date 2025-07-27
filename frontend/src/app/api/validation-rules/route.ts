import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://acceptable-wisdom-production-ac06.up.railway.app';

// Force dynamic rendering since we use request.headers
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    // For now, return mock data since the backend endpoint doesn't exist yet
    console.log("📋 Returning mock validation rules data");
    return NextResponse.json({
      success: true,
      rules: [
        {
          id: "color_matching",
          name: "Color Matching",
          description: "Ensure colors complement each other",
          enabled: true,
          priority: "high"
        },
        {
          id: "occasion_appropriate",
          name: "Occasion Appropriate",
          description: "Match outfit to the occasion",
          enabled: true,
          priority: "high"
        },
        {
          id: "seasonal_appropriate",
          name: "Seasonal Appropriate",
          description: "Consider weather and season",
          enabled: true,
          priority: "medium"
        },
        {
          id: "style_coherence",
          name: "Style Coherence",
          description: "Maintain consistent style throughout",
          enabled: true,
          priority: "medium"
        }
      ],
      message: "Mock validation rules (backend endpoint not yet implemented)"
    });
  } catch (error) {
    console.error('Error fetching validation rules:', error);
    return NextResponse.json(
      { error: 'Failed to fetch validation rules', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
