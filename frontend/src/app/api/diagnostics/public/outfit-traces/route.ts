import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    // For now, return mock outfit traces data since the backend endpoint doesn't exist yet
    console.log("🔍 Returning mock outfit traces data");
    return NextResponse.json({
      success: true,
      traces: [
        {
          id: "trace_001",
          outfit_id: "outfit_123",
          user_id: "user_456",
          timestamp: new Date().toISOString(),
          action: "generated",
          metadata: {
            style: "casual",
            occasion: "weekend",
            weather: "sunny"
          },
          performance: {
            generation_time: "2.3s",
            user_rating: 4.5,
            feedback: "positive"
          }
        },
        {
          id: "trace_002",
          outfit_id: "outfit_124",
          user_id: "user_456",
          timestamp: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
          action: "viewed",
          metadata: {
            style: "business",
            occasion: "work",
            weather: "cloudy"
          },
          performance: {
            view_time: "45s",
            user_rating: 3.8,
            feedback: "neutral"
          }
        }
      ],
      summary: {
        total_traces: 2,
        average_rating: 4.15,
        most_popular_style: "casual",
        generation_success_rate: "95%"
      },
      message: "Mock outfit traces (backend endpoint not yet implemented)"
    });
  } catch (error) {
    console.error('Error fetching outfit traces:', error);
    return NextResponse.json(
      { 
        error: 'Failed to fetch outfit traces',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
} 