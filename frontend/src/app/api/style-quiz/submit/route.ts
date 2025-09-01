import { NextResponse } from 'next/server';
import { NextRequest } from 'next/server';

// Simple JWT token decoder for client-side tokens
function decodeFirebaseToken(token: string) {
  try {
    // Firebase JWT tokens have 3 parts separated by dots
    const parts = token.split('.');
    if (parts.length !== 3) {
      throw new Error('Invalid token format');
    }

    // Decode the payload (second part)
    const payload = parts[1];
    
    // Convert URL-safe base64 to standard base64
    const standardBase64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    
    // Add padding if needed
    const paddedBase64 = standardBase64 + '='.repeat((4 - standardBase64.length % 4) % 4);
    
    // Decode the base64 string
    const decodedPayload = atob(paddedBase64);
    
    // Parse the JSON payload
    return JSON.parse(decodedPayload);
  } catch (error) {
    console.error('Error decoding token:', error);
    throw new Error('Invalid token');
  }
}

export async function POST(req: NextRequest) {
  try {
    const submission = await req.json();
    const userId = submission.userId || submission.user_id || 'demo-user';

    // Mock successful submission (in production, this would save to Firestore)
    console.log('Mock quiz submission:', {
      userId,
      answers: submission.answers,
      colorAnalysis: submission.colorAnalysis
    });

    return NextResponse.json({ 
      success: true,
      message: 'Style profile saved successfully (mock)',
      hybridStyleName: "Personal Style",
      quizResults: {
        aesthetic_scores: { "classic": 0.6, "sophisticated": 0.4 },
        color_season: "warm_spring",
        body_type: "rectangle",
        style_preferences: { "classic": 0.7, "minimalist": 0.3 }
      },
      colorAnalysis: submission.colorAnalysis || null
    });
  } catch (error) {
    console.error('Error processing quiz submission:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to process quiz submission',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
} 