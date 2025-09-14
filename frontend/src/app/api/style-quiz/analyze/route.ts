import { NextRequest, NextResponse } from 'next/server';

// Function to calculate quiz results (matching frontend logic)
function calculateQuizResults(answers: any[]) {
  console.log('🎯 [Persona] User answers:', answers.reduce((acc, answer) => {
    acc[answer.question_id] = answer.selected_option;
    return acc;
  }, {}));

  // Score each persona based on quiz answers
  const personaScores: Record<string, number> = {
    architect: 0,
    strategist: 0,
    innovator: 0,
    classic: 0,
    wanderer: 0,
    rebel: 0,
    connoisseur: 0,
    modernist: 0
  };

  // Analyze visual style preferences from quiz answers
  const stylePreferences: Record<string, number> = {};
  answers.forEach(answer => {
    // This is a simplified version - in reality we'd need the full QUIZ_QUESTIONS array
    if (answer.question_id.startsWith('style_item_') && answer.selected_option === 'Yes') {
      // Extract style name from question ID or use a mapping
      const styleName = answer.question_id.replace('style_item_', '').replace(/_/g, ' ');
      stylePreferences[styleName] = (stylePreferences[styleName] || 0) + 1;
    }
  });

  console.log('🎯 [Persona] Style preferences:', stylePreferences);

  // Map style preferences to personas (simplified version)
  if (stylePreferences['minimalist'] || stylePreferences['clean minimal']) {
    personaScores.architect += 3;
    personaScores.modernist += 2;
  }
  if (stylePreferences['street style'] || stylePreferences['urban street']) {
    personaScores.rebel += 3;
    personaScores.strategist += 2;
  }
  if (stylePreferences['classic elegant']) {
    personaScores.classic += 3;
    personaScores.connoisseur += 2;
  }
  if (stylePreferences['old money']) {
    personaScores.connoisseur += 3;
    personaScores.classic += 2;
  }
  if (stylePreferences['bohemian'] || stylePreferences['vintage']) {
    personaScores.wanderer += 3;
    personaScores.innovator += 2;
  }
  if (stylePreferences['modern'] || stylePreferences['contemporary']) {
    personaScores.modernist += 3;
    personaScores.architect += 2;
  }

  // Add some randomness to prevent always getting strategist
  Object.keys(personaScores).forEach(persona => {
    personaScores[persona] += Math.random() * 0.5;
  });

  // Find the highest scoring persona
  const sortedPersonas = Object.entries(personaScores).sort(([,a], [,b]) => b - a);
  const selectedPersona = sortedPersonas[0][0];

  console.log('🎯 [Persona] Persona scores:', personaScores);
  console.log('🎯 [Persona] Sorted personas:', sortedPersonas);
  console.log('🎯 [Persona] Selected persona:', selectedPersona);

  return {
    persona: selectedPersona,
    persona_scores: personaScores,
    style_preferences: stylePreferences
  };
}

// Function to generate hybrid style name
function generateHybridStyleName(aestheticScores: Record<string, number>): string {
  const sortedAesthetics = Object.entries(aestheticScores)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 2);

  if (sortedAesthetics.length >= 2) {
    const [primary, secondary] = sortedAesthetics;
    const primaryName = primary[0].charAt(0).toUpperCase() + primary[0].slice(1);
    const secondaryName = secondary[0].charAt(0).toUpperCase() + secondary[0].slice(1);
    return `${primaryName} ${secondaryName}`;
  } else if (sortedAesthetics.length === 1) {
    const styleName = sortedAesthetics[0][0].charAt(0).toUpperCase() + sortedAesthetics[0][0].slice(1);
    return styleName;
  }
  return 'Personal Style';
}

export async function POST(req: NextRequest) {
  try {
    console.log('🔍 DEBUG: Style quiz analyze API called - MOCK VERSION');
    
    // Get the authorization header
    const authHeader = req.headers.get('authorization');
    if (!authHeader?.startsWith('Bearer ')) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Unauthorized',
          details: 'No authorization token provided'
        },
        { status: 401 }
      );
    }

    // Extract user info from Firebase token (client-side decoding)
    let userEmail = 'user@example.com';
    let userName = 'User';
    let userId = 'temp-user-id';
    
    try {
      const token = authHeader.replace('Bearer ', '');
      const tokenParts = token.split('.');
      if (tokenParts.length === 3) {
        // Firebase tokens use URL-safe base64, so we need to convert it
        const base64Payload = tokenParts[1].replace(/-/g, '+').replace(/_/g, '/');
        // Add padding if needed
        const paddedPayload = base64Payload + '='.repeat((4 - base64Payload.length % 4) % 4);
        const payload = JSON.parse(atob(paddedPayload));
        userEmail = payload.email || userEmail;
        userName = payload.name || payload.email?.split('@')[0] || userName;
        userId = payload.user_id || payload.sub || userId;
        console.log('🔍 DEBUG: Extracted user info from token:', { userEmail, userName, userId });
      }
    } catch (tokenError) {
      console.log('🔍 DEBUG: Could not decode token, using fallback values:', tokenError);
    }

    const submission = await req.json();
    console.log('🔍 DEBUG: Quiz submission:', submission);

    // Calculate quiz results
    const quizResults = calculateQuizResults(submission.answers);
    
    console.log('🔍 DEBUG: Quiz Results:', quizResults);

    // Return mock success response (no database saving in mock version)
    return NextResponse.json({ 
      success: true,
      message: 'Style profile analyzed successfully (mock version)',
      data: {
        persona: quizResults.persona,
        persona_scores: quizResults.persona_scores,
        style_preferences: quizResults.style_preferences
      }
    });
  } catch (error) {
    console.error('Error analyzing style profile:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to analyze style profile',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}