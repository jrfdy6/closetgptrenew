import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    // For now, return mock health data since the backend endpoint doesn't exist yet
    console.log("🏥 Returning mock health data");
    return NextResponse.json({
      success: true,
      status: "healthy",
      timestamp: new Date().toISOString(),
      services: {
        database: "operational",
        authentication: "operational",
        outfit_generation: "operational",
        analytics: "operational"
      },
      version: "1.0.0",
      uptime: "99.9%",
      message: "Mock health data (backend endpoint not yet implemented)"
    });
  } catch (error) {
    console.error('Error fetching health data:', error);
    return NextResponse.json(
      { 
        error: 'Failed to fetch health data',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
} 