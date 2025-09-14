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

    // Get user info from token for proper name/email
    let userName = 'Quiz User';
    let userEmail = 'quiz@example.com';
    
    try {
      const tokenPayload = decodeFirebaseToken(submission.token);
      console.log('🔍 [Quiz Submit] Token payload:', tokenPayload);
      userName = tokenPayload.name || tokenPayload.email?.split('@')[0] || 'Quiz User';
      userEmail = tokenPayload.email || 'quiz@example.com';
      console.log('🔍 [Quiz Submit] Extracted user info:', { userName, userEmail });
    } catch (e) {
      console.warn('Could not decode token for user info:', e);
    }

    // Map quiz answers to profile structure
    const profileUpdate = mapQuizAnswersToProfile(
      userAnswers, 
      submission.colorAnalysis, 
      submission.stylePreferences || [], 
      submission.colorPreferences || [],
      userName,
      userEmail
    );

    console.log('🔍 [Quiz Submit] Profile update data:', JSON.stringify(profileUpdate, null, 2));
    console.log('🔍 [Quiz Submit] User answers count:', Object.keys(userAnswers).length);
    console.log('🔍 [Quiz Submit] Style preferences:', submission.stylePreferences);
    console.log('🔍 [Quiz Submit] Color preferences:', submission.colorPreferences);
    console.log('🔍 [Quiz Submit] User info being saved:', { 
      name: profileUpdate.name, 
      email: profileUpdate.email,
      userId: profileUpdate.userId 
    });

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
        throw new Error(`Backend profile update failed: ${backendResponse.status} - ${errorText}`);
      } else {
        const responseData = await backendResponse.json();
        console.log('✅ Successfully saved profile to backend:', responseData);
        console.log('✅ Profile fields saved:', Object.keys(responseData));
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
  colorPreferences: string[],
  userName: string = 'Quiz User',
  userEmail: string = 'quiz@example.com'
) {
  // Calculate style personality scores based on preferences
  const stylePersonality = calculateStylePersonality(stylePreferences, userAnswers);
  
  // Determine the style persona based on quiz answers
  const determinedPersona = determineStylePersona(userAnswers, stylePreferences);
  
  // Map basic profile fields
  const profileUpdate: any = {
    // Required fields for backend
    name: userName,
    email: userEmail,
    
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
    // Add persona data
    stylePersona: {
      id: determinedPersona.id,
      name: determinedPersona.name,
      tagline: determinedPersona.tagline,
      description: determinedPersona.description,
      styleMission: determinedPersona.styleMission,
      traits: determinedPersona.traits,
      examples: determinedPersona.examples
    },
    createdAt: Math.floor(Date.now() / 1000), // Unix timestamp in seconds
    updatedAt: Math.floor(Date.now() / 1000) // Unix timestamp in seconds
  };

  return profileUpdate;
}

// Determine style persona based on quiz answers (copied from onboarding)
function determineStylePersona(userAnswers: Record<string, string>, stylePreferences: string[]): any {
  const STYLE_PERSONAS: Record<string, any> = {
    architect: {
      id: "architect",
      name: "The Architect",
      tagline: "Clean lines. Bold vision. Timeless design.",
      description: "You approach fashion like an architect approaches buildings - with precision, intention, and a focus on form following function. Your style is structured, sophisticated, and built to last. You appreciate quality construction and aren't afraid to make a statement with clean, geometric lines.",
      styleMission: "Build your wardrobe like you'd design a building - with a strong foundation, thoughtful details, and pieces that stand the test of time.",
      examples: ["Zaha Hadid", "Tadao Ando", "Frank Gehry", "Norman Foster", "Rem Koolhaas"],
      traits: ["Clean lines", "Bold vision", "Timeless design", "Quality construction", "Geometric precision"],
      cta: "See My Plan Options →"
    },
    rebel: {
      id: "rebel",
      name: "The Rebel",
      tagline: "Bold statements. Unconventional choices. Authentic expression.",
      description: "You don't follow trends - you create them. Your style is bold, unconventional, and authentically you. You're not afraid to mix unexpected pieces, experiment with color, or wear something that makes people look twice. Your fashion choices are a form of self-expression and rebellion against the ordinary.",
      styleMission: "Break the rules, set your own trends, and wear what makes you feel most like yourself. Don't be afraid to stand out.",
      examples: ["David Bowie", "Grace Jones", "Prince", "Frida Kahlo", "Alexander McQueen"],
      traits: ["Bold statements", "Unconventional choices", "Authentic expression", "Rule breaking", "Trend setting"],
      cta: "See My Plan Options →"
    },
    connoisseur: {
      id: "connoisseur",
      name: "The Connoisseur",
      tagline: "Refined taste. Luxury details. Quiet confidence.",
      description: "You have an eye for quality and appreciate the finer things in life. Your style is sophisticated, understated, and built on investment pieces that speak to your refined taste. You understand that true luxury is in the details, not the labels.",
      styleMission: "Curate your collection with intention. Focus on exceptional pieces that will last decades and don't be afraid to invest in quality over quantity.",
      examples: ["Meghan Markle", "Blake Lively", "Ryan Reynolds", "Henry Cavill", "Cate Blanchett"],
      traits: ["Refined taste", "Quality over quantity", "Luxury details", "Quiet confidence", "Investment pieces"],
      cta: "See My Plan Options →"
    },
    modernist: {
      id: "modernist",
      name: "The Modernist",
      tagline: "Clean lines. Contemporary edge. Future-focused.",
      description: "You're drawn to clean, contemporary design and appreciate the intersection of fashion and function. Your style is modern, streamlined, and forward-thinking. You value versatility and pieces that work across different contexts while maintaining a sleek, contemporary aesthetic.",
      styleMission: "Build a wardrobe that's both functional and fashionable. Focus on versatile pieces with clean lines and don't be afraid to experiment with modern silhouettes.",
      examples: ["Hailey Bieber", "Kendall Jenner", "Timothée Chalamet", "Harry Styles", "Anya Taylor-Joy"],
      traits: ["Clean lines", "Contemporary edge", "Functional fashion", "Versatile pieces", "Future-focused"],
      cta: "See My Plan Options →"
    }
  };

  // Score each persona based on quiz answers
  const personaScores: Record<string, number> = {
    architect: 0,
    rebel: 0,
    connoisseur: 0,
    modernist: 0
  };

  // Map style preferences to personas
  if (stylePreferences.includes('Minimalist') || stylePreferences.includes('Clean Minimal')) {
    personaScores.architect += 3;
    personaScores.modernist += 2;
  }
  if (stylePreferences.includes('Street Style') || stylePreferences.includes('Urban Street')) {
    personaScores.rebel += 3;
  }
  if (stylePreferences.includes('Classic Elegant')) {
    personaScores.connoisseur += 2;
  }
  if (stylePreferences.includes('Old Money')) {
    personaScores.connoisseur += 3;
  }
  if (stylePreferences.includes('Cottagecore') || stylePreferences.includes('Natural Boho')) {
    personaScores.rebel += 1;
  }

  // Daily activities scoring
  if (userAnswers.daily_activities === 'Office work and meetings') {
    personaScores.connoisseur += 2;
    personaScores.architect += 1;
  }
  if (userAnswers.daily_activities === 'Creative work and casual meetings') {
    personaScores.modernist += 2;
    personaScores.rebel += 1;
  }
  if (userAnswers.daily_activities === 'Active lifestyle and sports') {
    personaScores.rebel += 2;
  }
  if (userAnswers.daily_activities === 'Mix of everything') {
    personaScores.modernist += 3;
  }

  // Style elements scoring
  if (userAnswers.style_elements === 'Clean lines and minimal details') {
    personaScores.architect += 3;
    personaScores.modernist += 2;
  }
  if (userAnswers.style_elements === 'Rich textures and patterns') {
    personaScores.connoisseur += 3;
  }
  if (userAnswers.style_elements === 'Classic and timeless pieces') {
    personaScores.connoisseur += 2;
    personaScores.architect += 1;
  }
  if (userAnswers.style_elements === 'Bold and statement pieces') {
    personaScores.rebel += 3;
  }

  // Find the highest scoring persona
  const sortedPersonas = Object.entries(personaScores)
    .sort(([,a], [,b]) => b - a);
  
  const topPersona = sortedPersonas[0][0];
  
  console.log('🎯 [Quiz Submit] Persona scores:', personaScores);
  console.log('🎯 [Quiz Submit] Selected persona:', topPersona);
  
  return STYLE_PERSONAS[topPersona] || STYLE_PERSONAS.rebel;
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