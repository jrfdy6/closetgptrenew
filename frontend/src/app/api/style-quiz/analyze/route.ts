import { NextRequest, NextResponse } from 'next/server';

// Function to calculate quiz results (matching backend logic)
function calculateQuizResults(answers: any[]) {
  const aestheticScores: Record<string, number> = {};
  const colorScores: Record<string, number> = {};
  const bodyTypeScores: Record<string, number> = {};
  const styleScores: Record<string, number> = {};

  // Quiz questions mapping (matching the frontend questions)
  const quizQuestions = [
    {
      id: "movie_vibe",
      category: "aesthetic",
      options: [
        { text: "Classic Hollywood Glamour", scores: { "classic": 0.8, "sophisticated": 0.6, "romantic": 0.4 } },
        { text: "Indie Romance", scores: { "romantic": 0.8, "bohemian": 0.6, "vintage": 0.4 } },
        { text: "Minimalist Scandinavian", scores: { "minimalist": 0.9, "sophisticated": 0.5, "comfortable": 0.3 } },
        { text: "Urban Street Style", scores: { "streetwear": 0.8, "edgy": 0.6, "athletic": 0.4 } }
      ]
    },
    {
      id: "color_preference",
      category: "color",
      options: [
        { text: "Warm & Fresh", scores: { "warm_spring": 0.9, "warm_autumn": 0.7 } },
        { text: "Soft & Cool", scores: { "cool_summer": 0.9, "cool_spring": 0.7 } },
        { text: "Rich & Deep", scores: { "cool_winter": 0.9, "warm_winter": 0.7 } },
        { text: "Earthy & Warm", scores: { "warm_autumn": 0.9, "cool_autumn": 0.7 } }
      ]
    },
    {
      id: "silhouette_preference",
      category: "fit",
      options: [
        { text: "Fitted & Structured", scores: { "hourglass": 0.8, "rectangle": 0.6 } },
        { text: "Flowy & Relaxed", scores: { "pear": 0.8, "apple": 0.6 } },
        { text: "Balanced & Proportional", scores: { "rectangle": 0.8, "hourglass": 0.6 } },
        { text: "Dramatic & Statement", scores: { "inverted_triangle": 0.8, "triangle": 0.6 } }
      ]
    },
    {
      id: "daily_activities",
      category: "lifestyle",
      options: [
        { text: "Office work and meetings", scores: { "professional": 0.8, "classic": 0.6, "sophisticated": 0.4 } },
        { text: "Creative work and casual meetings", scores: { "bohemian": 0.7, "minimalist": 0.5, "comfortable": 0.3 } },
        { text: "Active lifestyle and sports", scores: { "athletic": 0.8, "streetwear": 0.6, "comfortable": 0.4 } },
        { text: "Mix of everything", scores: { "versatile": 0.8, "comfortable": 0.6, "sophisticated": 0.4 } }
      ]
    },
    {
      id: "style_elements",
      category: "style",
      options: [
        { text: "Clean lines and minimal details", scores: { "minimalist": 0.9, "sophisticated": 0.6 } },
        { text: "Rich textures and patterns", scores: { "bohemian": 0.8, "romantic": 0.6 } },
        { text: "Classic and timeless pieces", scores: { "classic": 0.9, "preppy": 0.6 } },
        { text: "Bold and statement pieces", scores: { "edgy": 0.8, "streetwear": 0.6 } }
      ]
    }
  ];

  for (const answer of answers) {
    try {
      const question = quizQuestions.find(q => q.id === answer.question_id);
      if (!question) continue;

      const selectedOption = question.options.find(o => 
        o.text.toLowerCase() === answer.selected_option.toLowerCase()
      );
      if (!selectedOption) continue;

      // Update scores based on question category
      if (question.category === "aesthetic") {
        for (const [style, score] of Object.entries(selectedOption.scores)) {
          aestheticScores[style] = (aestheticScores[style] || 0) + score;
        }
      } else if (question.category === "color") {
        for (const [season, score] of Object.entries(selectedOption.scores)) {
          colorScores[season] = (colorScores[season] || 0) + score;
        }
      } else if (question.category === "fit") {
        for (const [bodyType, score] of Object.entries(selectedOption.scores)) {
          bodyTypeScores[bodyType] = (bodyTypeScores[bodyType] || 0) + score;
        }
      } else if (question.category === "style") {
        for (const [style, score] of Object.entries(selectedOption.scores)) {
          styleScores[style] = (styleScores[style] || 0) + score;
        }
      }
    } catch (error) {
      console.error('Error processing answer:', answer, error);
      continue;
    }
  }

  // Normalize scores
  function normalizeScores(scores: Record<string, number>): Record<string, number> {
    const total = Object.values(scores).reduce((sum, score) => sum + score, 0);
    if (total === 0) return scores;
    return Object.fromEntries(
      Object.entries(scores).map(([key, value]) => [key, value / total])
    );
  }

  // Determine color season
  const colorSeason = Object.keys(colorScores).length > 0 
    ? Object.entries(colorScores).reduce((a, b) => a[1] > b[1] ? a : b)[0]
    : null;

  // Determine body type
  const bodyType = Object.keys(bodyTypeScores).length > 0
    ? Object.entries(bodyTypeScores).reduce((a, b) => a[1] > b[1] ? a : b)[0]
    : null;

  return {
    aesthetic_scores: normalizeScores(aestheticScores),
    color_season: colorSeason,
    body_type: bodyType,
    style_preferences: normalizeScores(styleScores)
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
    
    // Generate hybrid style name
    const hybridStyleName = generateHybridStyleName(quizResults.aesthetic_scores);

    // Convert style preferences from scores object to array of top styles
    const topStyles = Object.entries(quizResults.style_preferences)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
      .map(([style]) => style);

    console.log('🔍 DEBUG: Quiz Results:', quizResults);
    console.log('🔍 DEBUG: Hybrid Style Name:', hybridStyleName);
    console.log('🔍 DEBUG: Top Styles:', topStyles);

    // Return mock success response (no database saving in mock version)
    return NextResponse.json({ 
      success: true,
      message: 'Style profile analyzed successfully (mock version)',
      data: {
        hybridStyleName,
        quizResults
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