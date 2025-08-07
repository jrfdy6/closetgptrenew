import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  try {
    console.log('🔍 DEBUG: Feedback user summary API route called');
    
    // For now, return empty data since this is a new user
    return NextResponse.json({
      success: true,
      summary: {
        totalFeedback: 0,
        positiveFeedback: 0,
        negativeFeedback: 0,
        averageRating: 0,
        recentFeedback: []
      }
    });
  } catch (error) {
    console.error('🔍 DEBUG: Error in feedback user summary:', error);
    return NextResponse.json(
      { error: 'Failed to fetch feedback summary', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 