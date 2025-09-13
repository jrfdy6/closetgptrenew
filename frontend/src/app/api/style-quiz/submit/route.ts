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

    // Extract user answers from submission
    const userAnswers = submission.answers.reduce((acc: Record<string, string>, answer: any) => {
      acc[answer.question_id] = answer.selected_option;
      return acc;
    }, {});

    // Map quiz answers to profile structure
    const profileUpdate = mapQuizAnswersToProfile(
      userAnswers, 
      submission.colorAnalysis, 
      submission.stylePreferences || [], 
      submission.colorPreferences || []
    );

    console.log('🔍 [Quiz Submit] Profile update data:', JSON.stringify(profileUpdate, null, 2));

    // Save to user profile via backend API directly
    try {
      console.log('🔍 [Quiz Submit] Attempting to save profile to backend...');
      console.log('🔍 [Quiz Submit] Backend URL:', process.env.BACKEND_URL || 'https://closetgptrenew-backend-production.up.railway.app');
      console.log('🔍 [Quiz Submit] Token present:', !!submission.token);
      
      const backendResponse = await fetch(`${process.env.BACKEND_URL || 'https://closetgptrenew-backend-production.up.railway.app'}/api/auth/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${submission.token || ''}`
        },
        body: JSON.stringify(profileUpdate)
      });

      console.log('🔍 [Quiz Submit] Backend response status:', backendResponse.status);
      
      if (!backendResponse.ok) {
        const errorText = await backendResponse.text();
        console.error('❌ Failed to save profile to backend:', backendResponse.status, errorText);
      } else {
        const responseData = await backendResponse.json();
        console.log('✅ Successfully saved profile to backend:', responseData);
      }
    } catch (apiError) {
      console.error('❌ Backend save failed:', apiError);
      
      // Fallback: Try to save directly to Firestore
      try {
        console.log('🔄 [Quiz Submit] Attempting Firestore fallback...');
        const { db } = await import('@/lib/firebase/config');
        const { doc, setDoc } = await import('firebase/firestore');
        
        const userRef = doc(db, 'users', userId);
        await setDoc(userRef, profileUpdate, { merge: true });
        console.log('✅ Successfully saved profile to Firestore fallback');
      } catch (firestoreError) {
        console.error('❌ Firestore fallback also failed:', firestoreError);
      }
    }

    console.log('Quiz submission processed:', {
      userId,
      profileUpdate,
      userAnswers
    });

    return NextResponse.json({ 
      success: true,
      message: 'Style profile saved successfully',
      hybridStyleName: "Personal Style", // Will be overridden by frontend
      quizResults: {
        aesthetic_scores: profileUpdate.stylePersonality || { "classic": 0.6, "sophisticated": 0.4 },
        color_season: userAnswers.skin_tone || "warm_spring",
        body_type: userAnswers.body_type_female || userAnswers.body_type_male || "rectangle",
        style_preferences: profileUpdate.stylePreferences || ["classic", "minimalist"]
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

// Map quiz answers to user profile structure
function mapQuizAnswersToProfile(
  userAnswers: Record<string, string>, 
  colorAnalysis: any, 
  stylePreferences: string[], 
  colorPreferences: string[]
) {
  // Calculate style personality scores based on preferences
  const stylePersonality = calculateStylePersonality(stylePreferences, userAnswers);
  
  // Map basic profile fields
  const profileUpdate: any = {
    // Required fields for backend
    name: 'Quiz User', // Will be updated when we have user info
    email: 'quiz@example.com', // Will be updated when we have user info
    
    // Quiz-specific fields
    gender: userAnswers.gender,
    bodyType: userAnswers.body_type_female || userAnswers.body_type_male || '',
    skinTone: userAnswers.skin_tone || null,
    measurements: {
      height: parseHeight(userAnswers.height),
      weight: parseWeight(userAnswers.weight),
      bodyType: userAnswers.body_type_female || userAnswers.body_type_male || '',
      skinTone: userAnswers.skin_tone || null,
      topSize: userAnswers.top_size || '',
      bottomSize: userAnswers.bottom_size || '',
      shoeSize: userAnswers.shoe_size || '',
      braSize: userAnswers.cup_size || ''
    },
    stylePreferences: stylePreferences,
    preferences: {
      style: stylePreferences,
      colors: colorPreferences,
      occasions: [userAnswers.daily_activities || '']
    },
    stylePersonality: stylePersonality,
    colorPalette: {
      primary: colorPreferences.slice(0, 3),
      secondary: colorPreferences.slice(3, 6),
      accent: colorPreferences.slice(6, 9),
      neutral: ['black', 'white', 'gray', 'beige'],
      avoid: []
    },
    updatedAt: Date.now()
  };

  return profileUpdate;
}

// Calculate style personality scores based on quiz answers
function calculateStylePersonality(stylePreferences: string[], userAnswers: Record<string, string>) {
  const scores = {
    classic: 0.5,
    modern: 0.5,
    creative: 0.5,
    minimal: 0.5,
    bold: 0.5
  };

  // Adjust scores based on style preferences
  stylePreferences.forEach(style => {
    switch (style) {
      case 'Classic Elegant':
      case 'Old Money':
        scores.classic += 0.3;
        scores.minimal += 0.1;
        break;
      case 'Street Style':
      case 'Urban Street':
        scores.bold += 0.3;
        scores.creative += 0.2;
        break;
      case 'Minimalist':
      case 'Clean Minimal':
        scores.minimal += 0.3;
        scores.classic += 0.1;
        break;
      case 'Cottagecore':
      case 'Natural Boho':
        scores.creative += 0.2;
        scores.modern += 0.1;
        break;
    }
  });

  // Adjust based on daily activities
  if (userAnswers.daily_activities === 'Office work and meetings') {
    scores.classic += 0.2;
    scores.minimal += 0.1;
  } else if (userAnswers.daily_activities === 'Creative work and casual meetings') {
    scores.creative += 0.2;
    scores.modern += 0.1;
  }

  // Adjust based on style elements
  if (userAnswers.style_elements === 'Clean lines and minimal details') {
    scores.minimal += 0.2;
    scores.classic += 0.1;
  } else if (userAnswers.style_elements === 'Bold and statement pieces') {
    scores.bold += 0.2;
    scores.creative += 0.1;
  }

  // Normalize scores to 0-1 range
  Object.keys(scores).forEach(key => {
    scores[key] = Math.max(0, Math.min(1, scores[key]));
  });

  return scores;
}

// Helper functions to parse measurements
function parseHeight(heightStr: string): number {
  if (!heightStr) return 0;
  // Convert height string to inches
  const match = heightStr.match(/(\d+)'(\d+)"/);
  if (match) {
    const feet = parseInt(match[1]);
    const inches = parseInt(match[2]);
    return feet * 12 + inches;
  }
  return 0;
}

function parseWeight(weightStr: string): number {
  if (!weightStr) return 0;
  // Extract number from weight range
  const match = weightStr.match(/(\d+)/);
  return match ? parseInt(match[1]) : 0;
} 